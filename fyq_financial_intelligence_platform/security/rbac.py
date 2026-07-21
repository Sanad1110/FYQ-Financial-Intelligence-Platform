"""
FYQ RBAC FRAMEWORK — نظام التحكم في الوصول بناءً على الأدوار
═════════════════════════════════════════════════════════════════
Role-Based Access Control | Permissions | Authorization
"""

from enum import Enum
from typing import Dict, List, Set
from database import UserRole


# ═════════════════════════════════════════════════════════════════
# PERMISSIONS — الصلاحيات
# ═════════════════════════════════════════════════════════════════

class Permission(Enum):
    """قائمة الصلاحيات المركزية"""
    
    # إدارة المستخدمين
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # إدارة المنظمات
    CREATE_ORGANIZATION = "create_organization"
    READ_ORGANIZATION = "read_organization"
    UPDATE_ORGANIZATION = "update_organization"
    DELETE_ORGANIZATION = "delete_organization"
    
    # إدارة التحليلات
    CREATE_ANALYSIS = "create_analysis"
    READ_ANALYSIS = "read_analysis"
    UPDATE_ANALYSIS = "update_analysis"
    DELETE_ANALYSIS = "delete_analysis"
    SUBMIT_ANALYSIS = "submit_analysis"
    APPROVE_ANALYSIS = "approve_analysis"
    REJECT_ANALYSIS = "reject_analysis"
    
    # تشغيل المحركات
    RUN_BUDGET_ENGINE = "run_budget_engine"
    RUN_FORECAST_ENGINE = "run_forecast_engine"
    RUN_KPI_ENGINE = "run_kpi_engine"
    RUN_VARIANCE_ENGINE = "run_variance_engine"
    RUN_RISK_ENGINE = "run_risk_engine"
    RUN_CONSOLIDATION_ENGINE = "run_consolidation_engine"
    RUN_SCENARIO_ENGINE = "run_scenario_engine"
    
    # التقارير والتصدير
    GENERATE_REPORTS = "generate_reports"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"
    
    # الإعدادات والنظام
    MANAGE_SETTINGS = "manage_settings"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_PERMISSIONS = "manage_permissions"


# ═════════════════════════════════════════════════════════════════
# ROLE-BASED PERMISSIONS — الصلاحيات حسب الأدوار
# ═════════════════════════════════════════════════════════════════

class RolePermissions:
    """تعريف الصلاحيات لكل دور"""
    
    PERMISSIONS_MAP: Dict[UserRole, Set[Permission]] = {
        
        # مسؤول النظام — كل الصلاحيات
        UserRole.ADMIN: {
            # المستخدمون
            Permission.CREATE_USER,
            Permission.READ_USER,
            Permission.UPDATE_USER,
            Permission.DELETE_USER,
            
            # المنظمات
            Permission.CREATE_ORGANIZATION,
            Permission.READ_ORGANIZATION,
            Permission.UPDATE_ORGANIZATION,
            Permission.DELETE_ORGANIZATION,
            
            # التحليلات
            Permission.CREATE_ANALYSIS,
            Permission.READ_ANALYSIS,
            Permission.UPDATE_ANALYSIS,
            Permission.DELETE_ANALYSIS,
            Permission.SUBMIT_ANALYSIS,
            Permission.APPROVE_ANALYSIS,
            Permission.REJECT_ANALYSIS,
            
            # المحركات
            Permission.RUN_BUDGET_ENGINE,
            Permission.RUN_FORECAST_ENGINE,
            Permission.RUN_KPI_ENGINE,
            Permission.RUN_VARIANCE_ENGINE,
            Permission.RUN_RISK_ENGINE,
            Permission.RUN_CONSOLIDATION_ENGINE,
            Permission.RUN_SCENARIO_ENGINE,
            
            # التقارير
            Permission.GENERATE_REPORTS,
            Permission.EXPORT_DATA,
            Permission.IMPORT_DATA,
            
            # الإعدادات
            Permission.MANAGE_SETTINGS,
            Permission.VIEW_AUDIT_LOGS,
            Permission.MANAGE_PERMISSIONS,
        },
        
        # مدير مالي — صلاحيات عالية
        UserRole.FINANCE_MANAGER: {
            # المستخدمون (قراءة فقط)
            Permission.READ_USER,
            
            # المنظمات
            Permission.READ_ORGANIZATION,
            Permission.UPDATE_ORGANIZATION,
            
            # التحليلات (كاملة)
            Permission.CREATE_ANALYSIS,
            Permission.READ_ANALYSIS,
            Permission.UPDATE_ANALYSIS,
            Permission.DELETE_ANALYSIS,
            Permission.SUBMIT_ANALYSIS,
            Permission.APPROVE_ANALYSIS,
            Permission.REJECT_ANALYSIS,
            
            # المحركات (كاملة)
            Permission.RUN_BUDGET_ENGINE,
            Permission.RUN_FORECAST_ENGINE,
            Permission.RUN_KPI_ENGINE,
            Permission.RUN_VARIANCE_ENGINE,
            Permission.RUN_RISK_ENGINE,
            Permission.RUN_CONSOLIDATION_ENGINE,
            Permission.RUN_SCENARIO_ENGINE,
            
            # التقارير
            Permission.GENERATE_REPORTS,
            Permission.EXPORT_DATA,
            Permission.IMPORT_DATA,
            
            # الإعدادات (قراءة فقط)
            Permission.VIEW_AUDIT_LOGS,
        },
        
        # محلل مالي — صلاحيات متوسطة
        UserRole.ANALYST: {
            # المستخدمون (قراءة فقط)
            Permission.READ_USER,
            
            # المنظمات (قراءة فقط)
            Permission.READ_ORGANIZATION,
            
            # التحليلات
            Permission.CREATE_ANALYSIS,
            Permission.READ_ANALYSIS,
            Permission.UPDATE_ANALYSIS,
            Permission.SUBMIT_ANALYSIS,
            
            # المحركات (كاملة)
            Permission.RUN_BUDGET_ENGINE,
            Permission.RUN_FORECAST_ENGINE,
            Permission.RUN_KPI_ENGINE,
            Permission.RUN_VARIANCE_ENGINE,
            Permission.RUN_RISK_ENGINE,
            Permission.RUN_CONSOLIDATION_ENGINE,
            Permission.RUN_SCENARIO_ENGINE,
            
            # التقارير
            Permission.GENERATE_REPORTS,
            Permission.EXPORT_DATA,
            Permission.IMPORT_DATA,
        },
        
        # مشاهد فقط — صلاحيات محدودة
        UserRole.VIEWER: {
            # المستخدمون (قراءة فقط)
            Permission.READ_USER,
            
            # المنظمات (قراءة فقط)
            Permission.READ_ORGANIZATION,
            
            # التحليلات (قراءة فقط)
            Permission.READ_ANALYSIS,
            
            # التقارير (قراءة فقط)
            Permission.GENERATE_REPORTS,
        },
    }
    
    @staticmethod
    def get_permissions(role: UserRole) -> Set[Permission]:
        """الحصول على الصلاحيات لدور معين"""
        return RolePermissions.PERMISSIONS_MAP.get(role, set())
    
    @staticmethod
    def has_permission(role: UserRole, permission: Permission) -> bool:
        """التحقق من وجود صلاحية معينة"""
        return permission in RolePermissions.get_permissions(role)


# ═════════════════════════════════════════════════════════════════
# AUTHORIZATION MANAGER — مدير التفويض
# ═════════════════════════════════════════════════════════════════

class AuthorizationManager:
    """مدير التفويض والتحكم في الوصول"""
    
    def __init__(self, user_role: UserRole):
        self.user_role = user_role
        self.permissions = RolePermissions.get_permissions(user_role)
    
    def can_perform(self, permission: Permission) -> bool:
        """التحقق من إمكانية تنفيذ إجراء معين"""
        return permission in self.permissions
    
    def require_permission(self, permission: Permission) -> bool:
        """التحقق من الصلاحية (يرفع استثناء إذا لم تكن موجودة)"""
        if not self.can_perform(permission):
            raise PermissionError(
                f"المستخدم ذو الدور '{self.user_role.value}' لا يملك صلاحية '{permission.value}'"
            )
        return True
    
    def get_allowed_actions(self) -> Dict[str, List[str]]:
        """الحصول على قائمة الإجراءات المسموحة"""
        actions = {}
        
        # تجميع الصلاحيات حسب الفئة
        for perm in self.permissions:
            perm_name = perm.value
            
            if perm_name.startswith('create_'):
                category = 'create'
            elif perm_name.startswith('read_'):
                category = 'read'
            elif perm_name.startswith('update_'):
                category = 'update'
            elif perm_name.startswith('delete_'):
                category = 'delete'
            elif perm_name.startswith('run_'):
                category = 'engines'
            elif perm_name.startswith('approve_') or perm_name.startswith('reject_') or perm_name.startswith('submit_'):
                category = 'workflow'
            elif perm_name.startswith('manage_') or perm_name.startswith('view_'):
                category = 'admin'
            else:
                category = 'other'
            
            if category not in actions:
                actions[category] = []
            
            actions[category].append(perm_name)
        
        return actions


# ═════════════════════════════════════════════════════════════════
# RESOURCE-LEVEL ACCESS CONTROL — التحكم في الوصول على مستوى المورد
# ═════════════════════════════════════════════════════════════════

class ResourceAccessControl:
    """التحكم في الوصول على مستوى المورد (Analysis Session, etc.)"""
    
    @staticmethod
    def can_access_analysis(user_id: str, user_role: UserRole, 
                           analysis_owner_id: str, organization_id: str) -> bool:
        """التحقق من إمكانية الوصول إلى تحليل معين"""
        
        # المسؤول يمكنه الوصول إلى كل شيء
        if user_role == UserRole.ADMIN:
            return True
        
        # مدير مالي يمكنه الوصول إلى تحليلات منظمته
        if user_role == UserRole.FINANCE_MANAGER:
            return True  # يتم التحقق من المنظمة في الـ API
        
        # محلل يمكنه الوصول إلى تحليلاته فقط أو المعتمدة
        if user_role == UserRole.ANALYST:
            return user_id == analysis_owner_id
        
        # مشاهد يمكنه الوصول إلى التحليلات المعتمدة فقط
        if user_role == UserRole.VIEWER:
            return True  # يتم التحقق من الحالة في الـ API
        
        return False
    
    @staticmethod
    def can_modify_analysis(user_id: str, user_role: UserRole, 
                           analysis_owner_id: str, analysis_status: str) -> bool:
        """التحقق من إمكانية تعديل تحليل معين"""
        
        # المسؤول يمكنه تعديل أي شيء
        if user_role == UserRole.ADMIN:
            return True
        
        # مدير مالي يمكنه تعديل التحليلات في حالة المسودة أو المرفوضة
        if user_role == UserRole.FINANCE_MANAGER:
            return analysis_status in ['draft', 'rejected']
        
        # محلل يمكنه تعديل تحليلاته في حالة المسودة فقط
        if user_role == UserRole.ANALYST:
            return user_id == analysis_owner_id and analysis_status == 'draft'
        
        # مشاهد لا يمكنه تعديل أي شيء
        return False
    
    @staticmethod
    def can_approve_analysis(user_role: UserRole) -> bool:
        """التحقق من إمكانية الموافقة على تحليل"""
        return user_role in [UserRole.ADMIN, UserRole.FINANCE_MANAGER]
    
    @staticmethod
    def can_reject_analysis(user_role: UserRole) -> bool:
        """التحقق من إمكانية رفض تحليل"""
        return user_role in [UserRole.ADMIN, UserRole.FINANCE_MANAGER]


# ═════════════════════════════════════════════════════════════════
# AUDIT DECORATOR — ديكوريتور التدقيق
# ═════════════════════════════════════════════════════════════════

def require_permission(permission: Permission):
    """ديكوريتور للتحقق من الصلاحيات"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # يتم استخراج المستخدم من السياق (يتم تمريره في الـ kwargs)
            user_role = kwargs.get('user_role')
            if not user_role:
                raise ValueError("user_role مطلوب في kwargs")
            
            auth_manager = AuthorizationManager(user_role)
            auth_manager.require_permission(permission)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ═════════════════════════════════════════════════════════════════
# PERMISSION MATRIX — مصفوفة الصلاحيات
# ═════════════════════════════════════════════════════════════════

def get_permission_matrix() -> Dict[str, Dict[str, bool]]:
    """الحصول على مصفوفة الصلاحيات الكاملة"""
    matrix = {}
    
    for role in UserRole:
        matrix[role.value] = {}
        permissions = RolePermissions.get_permissions(role)
        
        for perm in Permission:
            matrix[role.value][perm.value] = perm in permissions
    
    return matrix
