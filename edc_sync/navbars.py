from edc_navbar import Navbar, NavbarItem, site_navbars


edc_sync = Navbar(name='edc_sync')

edc_sync.append_item(
    NavbarItem(name='synchronization',
               label='Data Synchronization',
               fa_icon='fa-exchange',
               url_name='edc_sync:home_url'))

site_navbars.register(edc_sync)
