"""
FYQ DATABASE LAYER — طبقة البيانات المتقدمة
═════════════════════════════════════════════════════════════════
ORM Models | Persistence | Query Interface | Data Integrity
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid


# ═════════════════════════════════════════════════════════════════
# ENUMS — التعريفات المركزية
# ═════════════════════════════════════════════════════════════════

class WorkflowStatus(Enum):
    """حالات سير العمل"""
    DRAFT = "draft"                    # مسودة
    IN_REVIEW = "in_review"            # قيد المراجعة
    APPROVED = "approved"              # معتمد
    REJECTED = "rejected"              # مرفوض
    ARCHIVED = "archived"              # مؤرشف


class UserRole(Enum):
    """أدوار المستخدمين"""
    ADMIN = "admin"                    # مسؤول النظام
    FINANCE_MANAGER = "finance_manager" # مدير مالي
    ANALYST = "analyst"                # محلل مالي
    VIEWER = "viewer"                  # مشاهد فقط


class EngineType(Enum):
    """أنواع المحركات"""
    BUDGET = "budget"
    FORECAST = "forecast"
    KPI = "kpi"
    VARIANCE = "variance"
    RISK = "risk"
    CONSOLIDATION = "consolidation"
    SCENARIO = "scenario"


# ═════════════════════════════════════════════════════════════════
# MODELS — نماذج البيانات
# ═════════════════════════════════════════════════════════════════

@dataclass
class User:
    """نموذج المستخدم"""
    id: str
    username: str
    email: str
    role: UserRole
    password_hash: str
    created_at: str
    updated_at: str
    is_active: bool = True
    
    @staticmethod
    def hash_password(password: str) -> str:
        """تجزئة كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()


@dataclass
class Organization:
    """نموذج المنظمة"""
    id: str
    name: str
    sector: str
    registration_number: str
    currency: str
    fiscal_year_start: int  # شهر بداية السنة المالية (1-12)
    created_at: str
    updated_at: str
    is_active: bool = True


@dataclass
class AnalysisSession:
    """جلسة التحليل"""
    id: str
    organization_id: str
    user_id: str
    name: str
    description: str
    status: WorkflowStatus
    created_at: str
    updated_at: str
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejection_reason: Optional[str] = None


@dataclass
class BudgetRecord:
    """سجل الموازنة"""
    id: str
    analysis_id: str
    category: str
    budgeted: float
    actual: float
    month: int
    year: int
    variance: float
    variance_pct: float
    created_at: str
    updated_at: str


@dataclass
class ForecastRecord:
    """سجل التنبؤ"""
    id: str
    analysis_id: str
    metric: str
    historical_data: str  # JSON
    forecast_values: str  # JSON
    forecast_method: str  # "linear" or "exponential"
    confidence_level: float
    created_at: str
    updated_at: str


@dataclass
class KPIRecord:
    """سجل مؤشر الأداء"""
    id: str
    analysis_id: str
    name: str
    value: float
    target: float
    unit: str
    threshold_red: Optional[float]
    threshold_yellow: Optional[float]
    status: str  # "GREEN", "YELLOW", "RED"
    achievement_pct: float
    created_at: str
    updated_at: str


@dataclass
class RiskRecord:
    """سجل المخاطرة"""
    id: str
    analysis_id: str
    name: str
    probability: float
    impact: float
    risk_score: float
    risk_level: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    mitigation: str
    created_at: str
    updated_at: str


@dataclass
class AuditLog:
    """سجل التدقيق"""
    id: str
    user_id: str
    organization_id: str
    action: str
    entity_type: str
    entity_id: str
    changes: str  # JSON
    timestamp: str
    ip_address: Optional[str] = None


# ═════════════════════════════════════════════════════════════════
# DATABASE MANAGER — مدير قاعدة البيانات
# ═════════════════════════════════════════════════════════════════

class DatabaseManager:
    """مدير قاعدة البيانات المركزي"""
    
    def __init__(self, db_path: str = 'fyq.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """الحصول على اتصال قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # جدول المنظمات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                sector TEXT,
                registration_number TEXT,
                currency TEXT DEFAULT 'SAR',
                fiscal_year_start INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # جدول جلسات التحليل
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                approved_by TEXT,
                approved_at TEXT,
                rejection_reason TEXT,
                FOREIGN KEY (organization_id) REFERENCES organizations(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (approved_by) REFERENCES users(id)
            )
        ''')
        
        # جدول سجلات الموازنة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_records (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                category TEXT NOT NULL,
                budgeted REAL NOT NULL,
                actual REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                variance REAL NOT NULL,
                variance_pct REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analysis_sessions(id)
            )
        ''')
        
        # جدول سجلات التنبؤ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecast_records (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                metric TEXT NOT NULL,
                historical_data TEXT NOT NULL,
                forecast_values TEXT NOT NULL,
                forecast_method TEXT NOT NULL,
                confidence_level REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analysis_sessions(id)
            )
        ''')
        
        # جدول سجلات مؤشرات الأداء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpi_records (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                target REAL NOT NULL,
                unit TEXT NOT NULL,
                threshold_red REAL,
                threshold_yellow REAL,
                status TEXT NOT NULL,
                achievement_pct REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analysis_sessions(id)
            )
        ''')
        
        # جدول سجلات المخاطر
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_records (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                name TEXT NOT NULL,
                probability REAL NOT NULL,
                impact REAL NOT NULL,
                risk_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                mitigation TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analysis_sessions(id)
            )
        ''')
        
        # جدول سجل التدقيق
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                organization_id TEXT NOT NULL,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                changes TEXT,
                timestamp TEXT NOT NULL,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (organization_id) REFERENCES organizations(id)
            )
        ''')
        
        # إنشاء الفهارس
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_org ON analysis_sessions(organization_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_user ON analysis_sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_budget_analysis ON budget_records(analysis_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kpi_analysis ON kpi_records(analysis_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_logs(organization_id)')
        
        conn.commit()
        conn.close()
    
    # ─── User Operations ───
    def create_user(self, username: str, email: str, role: UserRole, password: str) -> User:
        """إنشاء مستخدم جديد"""
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        password_hash = User.hash_password(password)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (id, username, email, role, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, email, role.value, password_hash, now, now))
        
        conn.commit()
        conn.close()
        
        return User(user_id, username, email, role, password_hash, now, now)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """الحصول على مستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return User(
            row['id'], row['username'], row['email'],
            UserRole(row['role']), row['password_hash'],
            row['created_at'], row['updated_at'], row['is_active']
        )
    
    # ─── Organization Operations ───
    def create_organization(self, name: str, sector: str, registration_number: str, 
                           currency: str = 'SAR', fiscal_year_start: int = 1) -> Organization:
        """إنشاء منظمة جديدة"""
        org_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO organizations (id, name, sector, registration_number, currency, fiscal_year_start, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (org_id, name, sector, registration_number, currency, fiscal_year_start, now, now))
        
        conn.commit()
        conn.close()
        
        return Organization(org_id, name, sector, registration_number, currency, fiscal_year_start, now, now)
    
    # ─── Analysis Session Operations ───
    def create_analysis_session(self, organization_id: str, user_id: str, 
                               name: str, description: str = '') -> AnalysisSession:
        """إنشاء جلسة تحليل جديدة"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_sessions 
            (id, organization_id, user_id, name, description, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, organization_id, user_id, name, description, WorkflowStatus.DRAFT.value, now, now))
        
        conn.commit()
        conn.close()
        
        return AnalysisSession(session_id, organization_id, user_id, name, description, 
                              WorkflowStatus.DRAFT, now, now)
    
    def update_analysis_status(self, session_id: str, status: WorkflowStatus, 
                              approved_by: Optional[str] = None, rejection_reason: Optional[str] = None):
        """تحديث حالة جلسة التحليل"""
        now = datetime.now().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status == WorkflowStatus.APPROVED:
            cursor.execute('''
                UPDATE analysis_sessions 
                SET status = ?, approved_by = ?, approved_at = ?, updated_at = ?
                WHERE id = ?
            ''', (status.value, approved_by, now, now, session_id))
        elif status == WorkflowStatus.REJECTED:
            cursor.execute('''
                UPDATE analysis_sessions 
                SET status = ?, rejection_reason = ?, updated_at = ?
                WHERE id = ?
            ''', (status.value, rejection_reason, now, session_id))
        else:
            cursor.execute('''
                UPDATE analysis_sessions 
                SET status = ?, updated_at = ?
                WHERE id = ?
            ''', (status.value, now, session_id))
        
        conn.commit()
        conn.close()
    
    # ─── Budget Operations ───
    def save_budget_record(self, analysis_id: str, category: str, budgeted: float, 
                          actual: float, month: int, year: int) -> BudgetRecord:
        """حفظ سجل موازنة"""
        record_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        variance = actual - budgeted
        variance_pct = (variance / budgeted * 100) if budgeted != 0 else 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO budget_records 
            (id, analysis_id, category, budgeted, actual, month, year, variance, variance_pct, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (record_id, analysis_id, category, budgeted, actual, month, year, variance, variance_pct, now, now))
        
        conn.commit()
        conn.close()
        
        return BudgetRecord(record_id, analysis_id, category, budgeted, actual, month, year, 
                           variance, variance_pct, now, now)
    
    def get_budget_records(self, analysis_id: str) -> List[BudgetRecord]:
        """الحصول على سجلات الموازنة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM budget_records WHERE analysis_id = ? ORDER BY month', (analysis_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [BudgetRecord(
            row['id'], row['analysis_id'], row['category'], row['budgeted'], row['actual'],
            row['month'], row['year'], row['variance'], row['variance_pct'], 
            row['created_at'], row['updated_at']
        ) for row in rows]
    
    # ─── KPI Operations ───
    def save_kpi_record(self, analysis_id: str, name: str, value: float, target: float,
                       unit: str, status: str, achievement_pct: float,
                       threshold_red: Optional[float] = None, 
                       threshold_yellow: Optional[float] = None) -> KPIRecord:
        """حفظ سجل مؤشر أداء"""
        record_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO kpi_records 
            (id, analysis_id, name, value, target, unit, threshold_red, threshold_yellow, status, achievement_pct, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (record_id, analysis_id, name, value, target, unit, threshold_red, threshold_yellow, 
              status, achievement_pct, now, now))
        
        conn.commit()
        conn.close()
        
        return KPIRecord(record_id, analysis_id, name, value, target, unit, threshold_red, 
                        threshold_yellow, status, achievement_pct, now, now)
    
    def get_kpi_records(self, analysis_id: str) -> List[KPIRecord]:
        """الحصول على سجلات مؤشرات الأداء"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM kpi_records WHERE analysis_id = ?', (analysis_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [KPIRecord(
            row['id'], row['analysis_id'], row['name'], row['value'], row['target'],
            row['unit'], row['threshold_red'], row['threshold_yellow'], row['status'],
            row['achievement_pct'], row['created_at'], row['updated_at']
        ) for row in rows]
    
    # ─── Risk Operations ───
    def save_risk_record(self, analysis_id: str, name: str, probability: float, 
                        impact: float, risk_score: float, risk_level: str, 
                        mitigation: str = '') -> RiskRecord:
        """حفظ سجل مخاطرة"""
        record_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO risk_records 
            (id, analysis_id, name, probability, impact, risk_score, risk_level, mitigation, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (record_id, analysis_id, name, probability, impact, risk_score, risk_level, mitigation, now, now))
        
        conn.commit()
        conn.close()
        
        return RiskRecord(record_id, analysis_id, name, probability, impact, risk_score, risk_level, mitigation, now, now)
    
    def get_risk_records(self, analysis_id: str) -> List[RiskRecord]:
        """الحصول على سجلات المخاطر"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM risk_records WHERE analysis_id = ?', (analysis_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [RiskRecord(
            row['id'], row['analysis_id'], row['name'], row['probability'], row['impact'],
            row['risk_score'], row['risk_level'], row['mitigation'], row['created_at'], row['updated_at']
        ) for row in rows]
    
    # ─── Audit Log Operations ───
    def log_audit(self, user_id: str, organization_id: str, action: str, 
                 entity_type: str, entity_id: str, changes: Dict = None, ip_address: str = None):
        """تسجيل إجراء في سجل التدقيق"""
        log_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        changes_json = json.dumps(changes) if changes else None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_logs 
            (id, user_id, organization_id, action, entity_type, entity_id, changes, timestamp, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (log_id, user_id, organization_id, action, entity_type, entity_id, changes_json, now, ip_address))
        
        conn.commit()
        conn.close()
    
    def get_audit_logs(self, organization_id: str, limit: int = 100) -> List[AuditLog]:
        """الحصول على سجلات التدقيق"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM audit_logs 
            WHERE organization_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (organization_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [AuditLog(
            row['id'], row['user_id'], row['organization_id'], row['action'],
            row['entity_type'], row['entity_id'], row['changes'], row['timestamp'], row['ip_address']
        ) for row in rows]
