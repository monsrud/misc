import enum


class Lan:
    """ This is the lan page"""

    def __init__(self, parent):
        self.parent = parent

    # TODO: complete lan page functionality

    def _navigate_to_page(self):
        """ Go to the status page """
        if self.parent.wd.current_url != self.parent.baseurl + '/#lan':
            element = self.parent.wd.find_element_by_id('lan-tab')
            element.click()
