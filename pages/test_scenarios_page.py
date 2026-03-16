"""
pages/test_scenarios_page.py
-----------------------------
Handles the three hardest browser interaction categories:
  1. JS Alerts / Confirms / Prompts   (TC07)
  2. iFrame switching                  (TC08)
  3. New tab and popup window handling (TC08)

Real element IDs confirmed from app HTML:
  #btn-simple-alert   #btn-confirm   #btn-prompt
  #confirm-result     #prompt-result
"""
from pages.base_page import BasePage
from config.locators import TestScenariosLocators as T


class TestScenariosPage(BasePage):
    PATH = "/test-scenarios"

    def open_scenarios(self) -> "TestScenariosPage":
        self.open(self.PATH)
        return self

    # ────────────────────────────────────────────────────────────────────────────
    # 1. ALERTS
    # LEARNING NOTE:
    #   JS dialogs (alert/confirm/prompt) are NOT part of the HTML DOM.
    #   Selenium handles them via driver.switch_to.alert.
    #   Always wait for the alert first — never assume it's instant.
    # ────────────────────────────────────────────────────────────────────────────

    def trigger_alert_and_accept(self) -> str:
        """Click 'Trigger Alert' → accept the JS alert → return its text."""
        self.click(T.ALERT_BTN)
        alert = self.wait.until_alert()
        text  = alert.text
        self.logger.info(f"Alert text: '{text}'")
        alert.accept()                           # click OK
        return text

    def trigger_confirm_and_accept(self) -> str:
        """Click 'Trigger Confirm' → accept → return dialog text."""
        self.click(T.CONFIRM_BTN)
        alert = self.wait.until_alert()
        text  = alert.text
        self.logger.info(f"Confirm text: '{text}' → accepting")
        alert.accept()                           # OK
        return text

    def trigger_confirm_and_dismiss(self) -> str:
        """Click 'Trigger Confirm' → dismiss → return dialog text."""
        self.click(T.CONFIRM_BTN)
        alert = self.wait.until_alert()
        text  = alert.text
        self.logger.info(f"Confirm text: '{text}' → dismissing")
        alert.dismiss()                          # Cancel
        return text

    def trigger_prompt_and_submit(self, input_text: str) -> str:
        """Click 'Trigger Prompt' → type text → accept → return dialog text."""
        self.click(T.PROMPT_BTN)
        alert = self.wait.until_alert()
        text  = alert.text
        self.logger.info(f"Prompt: '{text}' → entering '{input_text}'")
        alert.send_keys(input_text)
        alert.accept()
        return text

    def get_confirm_result(self) -> str:
        """Read the #confirm-result paragraph updated after dialog interaction."""
        return self.get_text(T.CONFIRM_RESULT)

    def get_prompt_result(self) -> str:
        """Read the #prompt-result paragraph updated after prompt interaction."""
        return self.get_text(T.PROMPT_RESULT)

    # ────────────────────────────────────────────────────────────────────────────
    # 2. iFRAME
    # LEARNING NOTE:
    #   An <iframe> is a nested browsing context — completely separate DOM.
    #   driver.find_element() can't see inside it until you switch.
    #   Always switch back to default_content() when done.
    # ────────────────────────────────────────────────────────────────────────────

    def get_iframe_body_text(self) -> str:
        """
        Switch into the page's iframe, read body text, return to main page.
        Returns the text found, or empty string if no iframe present.
        """
        try:
            self.wait.until_frame_and_switch(T.IFRAME)
            self.logger.info("Switched INTO iframe")

            # Grab whatever text is in the iframe body
            body = self.driver.find_element(*T.IFRAME_BODY_TEXT)
            content = body.text.strip()
            self.logger.info(f"iFrame content: '{content[:80]}'")
            return content

        except Exception as exc:
            self.logger.error(f"iFrame switch failed: {exc}")
            return ""

        finally:
            # ALWAYS return to main page — even if an exception occurred
            self.driver.switch_to.default_content()
            self.logger.info("Switched back to default content")

    # ────────────────────────────────────────────────────────────────────────────
    # 3. NEW TAB
    # LEARNING NOTE:
    #   Opening a new tab creates a new window handle.
    #   We collect handles before and after clicking, then switch to the new one.
    #   driver.window_handles is a list — the new handle is the one that
    #   wasn't there before.
    # ────────────────────────────────────────────────────────────────────────────

    def open_new_tab_and_switch(self) -> dict:
        """
        Click the new-tab button, wait for the window count to increase,
        switch to the new tab.
        Returns {"url": ..., "title": ...} of the new tab.
        """
        original_handles = self.driver.window_handles
        self.logger.info(f"Windows before click: {len(original_handles)}")

        self.click(T.NEW_TAB_BTN)
        self.wait.until_new_window(len(original_handles))

        new_handle = [h for h in self.driver.window_handles
                      if h not in original_handles][0]
        self.driver.switch_to.window(new_handle)
        self.logger.info(f"Switched to new tab: {self.driver.current_url}")

        return {"url": self.driver.current_url, "title": self.driver.title}

    def close_current_tab_and_return(self) -> None:
        """Close the current tab and switch back to the first window."""
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.logger.info("Closed tab, returned to main window")

    # ────────────────────────────────────────────────────────────────────────────
    # 4. POPUP WINDOW
    # LEARNING NOTE:
    #   Popups (window.open()) also create a new handle, same pattern as tabs.
    # ────────────────────────────────────────────────────────────────────────────

    def open_popup_and_switch(self) -> dict:
        """Open popup window, switch to it, return {url, title}."""
        original_handles = self.driver.window_handles
        self.click(T.POPUP_BTN)
        self.wait.until_new_window(len(original_handles))

        popup_handle = [h for h in self.driver.window_handles
                        if h not in original_handles][0]
        self.driver.switch_to.window(popup_handle)
        self.logger.info(f"Switched to popup: {self.driver.current_url}")
        return {"url": self.driver.current_url, "title": self.driver.title}

    def switch_to_main_window(self) -> None:
        """Switch back to the original (first) window handle."""
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.logger.info("Returned to main window")
