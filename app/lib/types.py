import enum

class TransactionType(enum.Enum):
    DELIVERY = "Delivery"
    DISCARD = "Discard"
    ATTEND_REQUEST = "Attend request"
    DENY_REQUEST = "Deny request"

class RequestStatus(enum.Enum):
    REQUESTED = "Requested"
    ATTENDED = "Attended"
    DENIED = "Denied"

class RequestType(enum.Enum):
    TOTAL = "Total"
    PARTIAL = "Partial"

class UserRole(enum.Enum):
    ADMIN = "Admin"
    REQUESTER = "Requester"
    MANAGER = "Manager"

class EmailType(enum.Enum):
    DENIED = "Denied"
    ACCEPTED = "Accepted"
    PENDING_APROVAL = "Pending Approval"