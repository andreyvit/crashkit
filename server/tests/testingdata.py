
import fixture
from fixture import DataSet

admin_user = 'andreyvit@gmail.com'

class AccountData(DataSet):
  class acme:
    permalink = "acme"
    name = "Acme Corp."

class ProductData(DataSet):
  class killerapp:
    account = AccountData.acme
    unique_name = 'killerapp'
    friendly_name = 'The Killer App'
    public_access = True

class LimitedBetaCandidateData(DataSet):
  class acmeceo_uninvited:
    email = 'ceo@acme.com'
    tech = 'Python'
  class acmeceo_invited(acmeceo_uninvited):
    invitation_code = 'qwe123'
    
class ServerConfigData(DataSet):
  class default:
    key_name = 'TheConfig'
    signup_email_text        = "Hello!"
    signup_email_subject     = "Welcome!"
    signup_email_unused_text = ""


from fixture import GoogleDatastoreFixture, DataSet
from fixture.style import NamedDataStyle
import models

the_gae_fixture = GoogleDatastoreFixture(env=models, style=NamedDataStyle())
