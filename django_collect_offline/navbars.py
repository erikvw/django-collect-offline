from edc_navbar import Navbar, NavbarItem, site_navbars


navbar = Navbar(name='django_collect_offline')

navbar.append_item(
    NavbarItem(name='synchronization',
               label='Offline Synchronization',
               fa_icon='fa-exchange',
               url_name='django_collect_offline:home_url'))

site_navbars.register(navbar)
