"""
FYQ WORKFLOW ENGINE — محرك سير العمل
═════════════════════════════════════════════════════════════════
State Machine | Transitions | Notifications | Audit Trail
"""

from enum import Enum
from typing import Dict, List, Optional, Callable
from datetime import datetime
from database import WorkflowStatus, DatabaseManager, AuditLog


# ═════════════════════════════════════════════════════════════════
# WORKFLOW STATE MACHINE — آلة الحالات
# ═════════════════════════════════════════════════════════════════

class WorkflowTransition:
    """انتقال في سير العمل"""
    
    def __init__(self, from_state: WorkflowStatus, to_state: WorkflowStatus, 
                 action: str, allowed_roles: List[str], 
                 pre_action: Optional[Callable] = None,
                 post_action: Optional[Callable] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.action = action
        self.allowed_roles = allowed_roles
        self.pre_action = pre_action
        self.post_action = post_action
    
    def is_allowed(self, user_role: str) -> bool:
        """التحقق من أن الدور مسموح به"""
        return user_role in self.allowed_roles


class WorkflowEngine:
    """محرك سير العمل"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.transitions = self._define_transitions()
        self.listeners: List[Callable] = []
    
    def _define_transitions(self) -> Dict[tuple, WorkflowTransition]:
        """تعريف انتقالات سير العمل"""
        transitions = {}
        
        # DRAFT → IN_REVIEW (تقديم التحليل)
        transitions[(WorkflowStatus.DRAFT, WorkflowStatus.IN_REVIEW)] = WorkflowTransition(
            from_state=WorkflowStatus.DRAFT,
            to_state=WorkflowStatus.IN_REVIEW,
            action="submit_for_review",
            allowed_roles=["analyst", "finance_manager", "admin"]
        )
        
        # IN_REVIEW → APPROVED (الموافقة)
        transitions[(WorkflowStatus.IN_REVIEW, WorkflowStatus.APPROVED)] = WorkflowTransition(
            from_state=WorkflowStatus.IN_REVIEW,
            to_state=WorkflowStatus.APPROVED,
            action="approve",
            allowed_roles=["finance_manager", "admin"]
        )
        
        # IN_REVIEW → REJECTED (الرفض)
        transitions[(WorkflowStatus.IN_REVIEW, WorkflowStatus.REJECTED)] = WorkflowTransition(
            from_state=WorkflowStatus.IN_REVIEW,
            to_state=WorkflowStatus.REJECTED,
            action="reject",
            allowed_roles=["finance_manager", "admin"]
        )
        
        # REJECTED → DRAFT (العودة إلى المسودة)
        transitions[(WorkflowStatus.REJECTED, WorkflowStatus.DRAFT)] = WorkflowTransition(
            from_state=WorkflowStatus.REJECTED,
            to_state=WorkflowStatus.DRAFT,
            action="resubmit",
            allowed_roles=["analyst", "finance_manager", "admin"]
        )
        
        # APPROVED → ARCHIVED (الأرشفة)
        transitions[(WorkflowStatus.APPROVED, WorkflowStatus.ARCHIVED)] = WorkflowTransition(
            from_state=WorkflowStatus.APPROVED,
            to_state=WorkflowStatus.ARCHIVED,
            action="archive",
            allowed_roles=["finance_manager", "admin"]
        )
        
        # DRAFT → ARCHIVED (الأرشفة المباشرة)
        transitions[(WorkflowStatus.DRAFT, WorkflowStatus.ARCHIVED)] = WorkflowTransition(
            from_state=WorkflowStatus.DRAFT,
            to_state=WorkflowStatus.ARCHIVED,
            action="archive",
            allowed_roles=["admin"]
        )
        
        return transitions
    
    def can_transition(self, from_state: WorkflowStatus, to_state: WorkflowStatus, 
                      user_role: str) -> bool:
        """التحقق من إمكانية الانتقال"""
        key = (from_state, to_state)
        
        if key not in self.transitions:
            return False
        
        transition = self.transitions[key]
        return transition.is_allowed(user_role)
    
    def execute_transition(self, analysis_id: str, from_state: WorkflowStatus, 
                          to_state: WorkflowStatus, user_id: str, user_role: str,
                          organization_id: str, rejection_reason: Optional[str] = None) -> bool:
        """تنفيذ انتقال في سير العمل"""
        
        # التحقق من إمكانية الانتقال
        if not self.can_transition(from_state, to_state, user_role):
            raise PermissionError(
                f"لا يمكن الانتقال من {from_state.value} إلى {to_state.value} بدور {user_role}"
            )
        
        # الحصول على تفاصيل الانتقال
        transition = self.transitions[(from_state, to_state)]
        
        # تنفيذ الإجراء السابق
        if transition.pre_action:
            transition.pre_action(analysis_id)
        
        # تحديث الحالة في قاعدة البيانات
        if to_state == WorkflowStatus.APPROVED:
            self.db.update_analysis_status(analysis_id, to_state, approved_by=user_id)
        elif to_state == WorkflowStatus.REJECTED:
            self.db.update_analysis_status(analysis_id, to_state, rejection_reason=rejection_reason)
        else:
            self.db.update_analysis_status(analysis_id, to_state)
        
        # تسجيل في سجل التدقيق
        self.db.log_audit(
            user_id=user_id,
            organization_id=organization_id,
            action=transition.action,
            entity_type="analysis_session",
            entity_id=analysis_id,
            changes={
                "from_state": from_state.value,
                "to_state": to_state.value,
                "rejection_reason": rejection_reason
            }
        )
        
        # تنفيذ الإجراء اللاحق
        if transition.post_action:
            transition.post_action(analysis_id)
        
        # إخطار المستمعين
        self._notify_listeners(analysis_id, from_state, to_state, user_id)
        
        return True
    
    def subscribe(self, listener: Callable):
        """الاشتراك في تغييرات الحالة"""
        self.listeners.append(listener)
    
    def _notify_listeners(self, analysis_id: str, from_state: WorkflowStatus, 
                         to_state: WorkflowStatus, user_id: str):
        """إخطار المستمعين بتغيير الحالة"""
        for listener in self.listeners:
            try:
                listener(analysis_id, from_state, to_state, user_id)
            except Exception as e:
                print(f"خطأ في المستمع: {e}")


# ═════════════════════════════════════════════════════════════════
# WORKFLOW NOTIFICATIONS — الإخطارات
# ═════════════════════════════════════════════════════════════════

class NotificationService:
    """خدمة الإخطارات"""
    
    @staticmethod
    def on_analysis_submitted(analysis_id: str, user_id: str):
        """عند تقديم التحليل للمراجعة"""
        # يمكن إضافة إرسال بريد إلكتروني أو إشعار
        print(f"📧 إخطار: تم تقديم التحليل {analysis_id} للمراجعة من قبل {user_id}")
    
    @staticmethod
    def on_analysis_approved(analysis_id: str, approver_id: str):
        """عند الموافقة على التحليل"""
        print(f"✅ إخطار: تمت الموافقة على التحليل {analysis_id} من قبل {approver_id}")
    
    @staticmethod
    def on_analysis_rejected(analysis_id: str, rejector_id: str, reason: str):
        """عند رفض التحليل"""
        print(f"❌ إخطار: تم رفض التحليل {analysis_id} من قبل {rejector_id}")
        print(f"   السبب: {reason}")


# ═════════════════════════════════════════════════════════════════
# WORKFLOW VALIDATOR — مدقق سير العمل
# ═════════════════════════════════════════════════════════════════

class WorkflowValidator:
    """مدقق سير العمل"""
    
    @staticmethod
    def validate_before_submission(analysis_id: str, db_manager: DatabaseManager) -> tuple[bool, str]:
        """التحقق من صحة التحليل قبل التقديم"""
        
        # التحقق من وجود بيانات الموازنة
        budget_records = db_manager.get_budget_records(analysis_id)
        if not budget_records:
            return False, "يجب إدخال بيانات الموازنة على الأقل"
        
        # التحقق من وجود مؤشرات الأداء
        kpi_records = db_manager.get_kpi_records(analysis_id)
        if not kpi_records:
            return False, "يجب إدخال مؤشرات الأداء على الأقل"
        
        # التحقق من وجود تقييم المخاطر
        risk_records = db_manager.get_risk_records(analysis_id)
        if not risk_records:
            return False, "يجب إدخال تقييم المخاطر على الأقل"
        
        return True, "التحليل جاهز للتقديم"
    
    @staticmethod
    def validate_before_approval(analysis_id: str, db_manager: DatabaseManager) -> tuple[bool, str]:
        """التحقق من صحة التحليل قبل الموافقة"""
        
        # التحقق من الصحة الأساسية
        is_valid, message = WorkflowValidator.validate_before_submission(analysis_id, db_manager)
        if not is_valid:
            return False, message
        
        # التحقق من عدم وجود انحرافات حرجة
        budget_records = db_manager.get_budget_records(analysis_id)
        critical_variances = [r for r in budget_records if abs(r.variance_pct) > 20]
        
        if critical_variances:
            return False, f"توجد {len(critical_variances)} انحرافات حرجة تتطلب توضيح"
        
        return True, "التحليل جاهز للموافقة"


# ═════════════════════════════════════════════════════════════════
# WORKFLOW HISTORY — سجل سير العمل
# ═════════════════════════════════════════════════════════════════

class WorkflowHistory:
    """سجل تاريخ سير العمل"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_analysis_history(self, analysis_id: str, organization_id: str) -> List[Dict]:
        """الحصول على سجل التغييرات للتحليل"""
        audit_logs = self.db.get_audit_logs(organization_id, limit=1000)
        
        # تصفية السجلات المتعلقة بالتحليل
        analysis_logs = [
            log for log in audit_logs 
            if log.entity_type == "analysis_session" and log.entity_id == analysis_id
        ]
        
        # تحويل إلى قاموس
        history = []
        for log in analysis_logs:
            history.append({
                'action': log.action,
                'user_id': log.user_id,
                'timestamp': log.timestamp,
                'changes': log.changes
            })
        
        return history
    
    def get_workflow_statistics(self, organization_id: str) -> Dict:
        """الحصول على إحصائيات سير العمل"""
        audit_logs = self.db.get_audit_logs(organization_id, limit=10000)
        
        stats = {
            'total_actions': len(audit_logs),
            'submissions': 0,
            'approvals': 0,
            'rejections': 0,
            'by_user': {}
        }
        
        for log in audit_logs:
            if log.action == 'submit_for_review':
                stats['submissions'] += 1
            elif log.action == 'approve':
                stats['approvals'] += 1
            elif log.action == 'reject':
                stats['rejections'] += 1
            
            if log.user_id not in stats['by_user']:
                stats['by_user'][log.user_id] = 0
            stats['by_user'][log.user_id] += 1
        
        return stats
