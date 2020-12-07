from django.contrib.auth import get_user_model
from django.test import Client, LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from crypto.models import RuleSet, get_or_create_crypto_model


class RegisterTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.selenium = webdriver.Firefox()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_register(self):
        self.selenium.get("{}/accounts/register/".format(self.live_server_url))
        username = self.selenium.find_element_by_id("id_username")
        email = self.selenium.find_element_by_id("id_email")
        password1 = self.selenium.find_element_by_id("id_password1")
        password2 = self.selenium.find_element_by_id("id_password2")

        submit = self.selenium.find_element_by_name("register")

        username.send_keys("test_user")
        email.send_keys("test@test.com")
        password1.send_keys("c0mpliCatedPassword")
        password2.send_keys("c0mpliCatedPassword")

        submit.click()

        assert "Thank you for registering" in self.selenium.page_source


class CryptoBotTestCases(LiveServerTestCase):
    TEST_USER_USERNAME = "test_user"
    TEST_USER_PASSWORD = "c0mplicaTedPassword"
    TEST_USER_EMAIL = "test@gmail.com"

    def setUp(self):
        # create Crypto
        self.ether = get_or_create_crypto_model(long_name="Ethereum", short_name="ETH")

        # create browser & login
        self.selenium = webdriver.Firefox()
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username=self.TEST_USER_USERNAME,
            password=self.TEST_USER_PASSWORD,
            email=self.TEST_USER_EMAIL,
        )

        self.client = Client()
        self.client.force_login(self.user)

        cookie = self.client.cookies["sessionid"]
        self.selenium.get(self.live_server_url + "/")
        self.selenium.add_cookie(
            {"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"}
        )
        self.selenium.refresh()
        self.selenium.get(self.live_server_url + "/")

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()

    def test_crypto_visible(self):
        assert "Ethereum" in self.selenium.page_source

    def test_add_ruleset(self):
        self.selenium.get(
            self.live_server_url
            + reverse("crypto:add_edit_ruleset", args=["Ethereum", 0])
        )
        name = self.selenium.find_element_by_id("id_name")
        name.send_keys("test-ruleset")
        submit = self.selenium.find_element_by_name("submit")
        submit.click()
        assert "test-ruleset" in self.selenium.page_source

    def test_add_rule(self):
        rs = RuleSet.objects.create(
            name="test2-ruleset",
            owner=self.user,
            type_of_ruleset="E",
            crypto=self.ether,
            id=100,
        )

        self.selenium.get(
            self.live_server_url + reverse("crypto:rules", args=["Ethereum", rs.id])
        )
        self.selenium.find_element_by_name("add_edit_rule").click()

        select = Select(self.selenium.find_element_by_name("rtype"))
        select.select_by_visible_text("Wait at least (minutes)")

        value = self.selenium.find_element_by_name("value")
        value.send_keys("5.0")

        submit = self.selenium.find_element_by_name("submit")
        submit.click()

        assert "Wait at least (minutes)" in self.selenium.page_source
        assert "5.0" in self.selenium.page_source
