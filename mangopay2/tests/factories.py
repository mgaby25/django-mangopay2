import datetime

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.conf import settings
from mangopay.constants import LEGAL_USER_TYPE_CHOICES, BANK_ACCOUNT_TYPE_CHOICES, DOCUMENTS_TYPE_CHOICES, \
    PAYIN_PAYMENT_TYPE

from money import Money
import factory

from ..models import (
    MangoPayNaturalUser, MangoPayBankAccount, MangoPayLegalUser, MangoPayWallet, MangoPayCardRegistration,
    MangoPayCard, MangoPayInRefund, MangoPayPayIn, MangoPayPage, MangoPayPayOut, MangoPayDocument, MangoPayTransfer
)


user_model_factory = getattr(
    settings,
    "AUTH_USER_MODEL_FACTORY",
    "mangopay2.tests.factories.UserFactory"
)


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'username{0}'.format(n))
    first_name = "Sven"
    last_name = "Svensons"
    is_active = True
    is_superuser = False
    is_staff = False
    email = "swede@swedishman.com"
    password = make_password("password")


class MangoPayNaturalUserFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayNaturalUser

    mangopay_id = None
    user = factory.SubFactory(user_model_factory)
    birthday = datetime.date(1989, 10, 20)
    country_of_residence = "US"
    nationality = "SE"
    address = None
    occupation = None
    income_range = None


class LightAuthenticationMangoPayNaturalUserFactory(MangoPayNaturalUserFactory):
    pass


class RegularAuthenticationMangoPayNaturalUserFactory(MangoPayNaturalUserFactory):

    address = "Somewhere over the rainbow"
    occupation = "Cobbler"
    income_range = '1'


class MangoPayLegalUserFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayLegalUser

    legal_person_type = LEGAL_USER_TYPE_CHOICES.business
    mangopay_id = None
    user = factory.SubFactory(user_model_factory)
    birthday = datetime.date(1989, 10, 20)
    country_of_residence = "US"
    nationality = "SE"
    address = None
    business_name = "FundedByMe AB"
    generic_business_email = "hello@fundedbyme.com"
    first_name = "Arno"
    last_name = "Smit"
    headquarters_address = None
    email = None


class LightAuthenticationMangoPayLegalUserFactory(MangoPayLegalUserFactory):
    pass


class RegularAuthenticationMangoPayLegalUserFactory(MangoPayLegalUserFactory):
    address = "Hammerby Sjostad 3"
    headquarters_address = "Sveavagen 1"
    email = "arno.smit@fundedbyme.com"


class MangoPayBankAccountFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayBankAccount

    mangopay_user = factory.SubFactory(MangoPayNaturalUserFactory)
    mangopay_id = None
    address = "Hundred Acre Wood"


class MangoPayIBANBankAccountFactory(MangoPayBankAccountFactory):
    account_type = BANK_ACCOUNT_TYPE_CHOICES.iban
    iban = "SE3550000000054910000003"
    country = "SE"
    bic = "DABAIE2D"


class MangoPayOTHERBankAccountFactory(MangoPayBankAccountFactory):
    account_type = BANK_ACCOUNT_TYPE_CHOICES.other
    account_number = "66112231"
    country = "SY"
    bic = "DABAIE2D"


class MangoPayUSBankAccountFactory(MangoPayBankAccountFactory):
    country = "US"
    account_type = BANK_ACCOUNT_TYPE_CHOICES.us
    account_number = "3327586"
    aba = "021000089"
    deposit_account_type = "CHECKING"


class MangoPayCardFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayCard

    mangopay_id = None
    expiration_date = None
    alias = None
    is_active = False
    is_valid = None


class MangoPayCardRegistrationFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayCardRegistration

    mangopay_id = None
    mangopay_user = factory.SubFactory(MangoPayNaturalUserFactory)
    mangopay_card = factory.SubFactory(MangoPayCardFactory)


class MangoPayDocumentFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayDocument

    mangopay_id = None
    mangopay_user = factory.SubFactory(MangoPayNaturalUserFactory)
    type = DOCUMENTS_TYPE_CHOICES.identity_proof
    status = None
    refused_reason_message = None


class MangoPayPageFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayPage

    document = factory.SubFactory(MangoPayDocumentFactory)
    file = "fake_file.jpg"


class MangoPayWalletFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayWallet

    mangopay_id = None
    mangopay_user = factory.SubFactory(MangoPayNaturalUserFactory)
    currency = "EUR"


class MangoPayPayOutFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayPayOut

    mangopay_id = None
    mangopay_user = factory.SubFactory(MangoPayNaturalUserFactory)
    mangopay_wallet = factory.SubFactory(MangoPayWalletFactory)
    mangopay_bank_account = factory.SubFactory(MangoPayBankAccountFactory)
    execution_date = None
    status = None
    debited_funds = Money(0, "EUR")
    fees = Money(0, "EUR")


class MangoPayPayInAbstractFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayPayIn
        abstract = True

    mangopay_id = None
    execution_date = None
    status = None
    result_code = None
    mangopay_user = factory.SubFactory(MangoPayNaturalUserFactory)
    mangopay_wallet = factory.SubFactory(MangoPayWalletFactory)


class MangoPayPayInFactory(MangoPayPayInAbstractFactory):

    class Meta:
        model = MangoPayPayIn

    mangopay_card = factory.SubFactory(MangoPayCardFactory)
    secure_mode_redirect_url = None
    payment_type = PAYIN_PAYMENT_TYPE.card

    @factory.post_generation
    def mangopay_refunds(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of refunds were passed in, use them
            for mangopay_refund in extracted:
                self.mangopay_refunds.add(mangopay_refund)


class MangoPayPayInBankWireFactory(MangoPayPayInAbstractFactory):

    class Meta:
        model = MangoPayPayIn

    wire_reference = None
    mangopay_bank_account = None
    type = PAYIN_PAYMENT_TYPE.bank_wire


class MangoPayInRefundFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayInRefund

    mangopay_id = None
    mangopay_user = factory.SubFactory(MangoPayNaturalUserFactory)
    mangopay_pay_in = factory.SubFactory(MangoPayPayInFactory)
    execution_date = None
    status = None
    result_code = None


class MangoPayTransferFactory(factory.DjangoModelFactory):

    class Meta:
        model = MangoPayTransfer

    mangopay_id = None
    mangopay_debited_wallet = factory.SubFactory(MangoPayWalletFactory)
    mangopay_credited_wallet = factory.SubFactory(MangoPayWalletFactory)
    debited_funds = Money(0, "EUR")
    execution_date = None
    status = None
    result_code = None
