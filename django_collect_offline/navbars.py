from edc_navbar import Navbar, NavbarItem, site_navbars


navbar = Navbar(name="django_collect_offline")

navbar.append_item(
    NavbarItem(
        name="collect_offline",
        label="Collect Offline",
        fa_icon="fa-exchange",
        url_name="django_collect_offline:home_url",
        codename="edc_navbar.nav_collect_offline",
    )
)

site_navbars.register(navbar)
