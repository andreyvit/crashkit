
from yoursway.web.handling import access_check, AccessDenied

@access_check
def requires_account_admin(handler):
  if not handler.account_access.is_admin_allowed():
    raise AccessDenied, "You need to be an administrator of the account to change its settings."
    
@access_check
def requires_signup_priv(self):
  if not self.person.is_signup_allowed():
    self.access_denied("You have not been invited into our beta program yet. Sorry, buddy.")
