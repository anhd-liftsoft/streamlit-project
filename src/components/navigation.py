import streamlit as st


class Navigation:
    """
    Navigation sidebar component for Streamlit apps.
    """

    def __init__(self, pages: list[dict[str, str]]) -> None:
        """Initialize Navigation with a list of pages.

        Args:
            pages: List of dictionaries, each dictionary contains:
                - 'file': File path of the page Python file.
                - 'title': Title displayed on the navigation.
        """
        self.pages = pages

    def render(self) -> None:
        """
        Create navigation sidebar from the provided list of pages
        and automatically run the page selected by the user.
        """
        ls = []
        for page in self.pages:
            ls.append(st.Page(page["file"], title=page["title"]))

        pg = st.navigation(ls)
        pg.run()
