import datetime
import os
import random
import time
import logging
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)

class HumanEmulator:
    """
    This class is used to emulate human-like typing and actions.
    """
        

    ## Human emulation parameters

    #Keystroke dynamics parameters 
    
    #Parameter UD: the interval between a key up and a key down
    TYPING_DELAY_RANGE = (0.073, 0.358)

    #Parameter H: the dwell time, how long the key is held down
    KEY_PRESS_DELAY_RANGE = (0.06, 0.126)

    #Chance of introducing a typo
    TYPO_CHANCE = 0.05

    #Longer interval, in case of a typing error
    LONG_PAUSE_RANGE = (0.2, 0.7)

    #Longer interval, in case of a typing error
    TYPO_CORRECTION_PAUSE_RANGE = (0.05, 0.15)

    #Click dynamics parameters

    #How long the click is held down
    CLICK_HOLD_RANGE = (0.05, 0.15)

    #Interval between clicks
    CLICK_PAUSE_RANGE = (1, 3)
    


    """
    For each key of a QWERTY keyboard, define the keys adjacent to it.
    This is used to emulate human-like typing, by introducing verosimilar typos.
    The assumption is that a typo is introduced between two adjacent keys.
    """
    ADJACENT_KEYS = {
        'a': 'qwsz',
        'b': 'vghn',
        'c': 'xdfv',
        'd': 'serfcx',
        'e': 'wsdfr',
        'f': 'dcvgtr',
        'g': 'fvbhyt',
        'h': 'gbnjuy',
        'i': 'ujklo',
        'j': 'hnmkiu',
        'k': 'jmloi',
        'l': 'kop',
        'm': 'njk',
        'n': 'bhjm',
        'o': 'iklp',
        'p': 'ol',
        'q': 'wa',
        'r': 'edft',
        's': 'wedxza',
        't': 'rfgy',
        'u': 'yhji',
        'v': 'cfgb',
        'w': 'qase',
        'x': 'zsdc',
        'y': 'tghu',
        'z': 'asx',
        '1': '2q',
        '2': '3wq1',
        '3': '4ew2',
        '4': '5re3',
        '5': '6tr4',
        '6': '7yt5',
        '7': '8uy6',
        '8': '9iu7',
        '9': '0oi8',
        '0': 'po9',
        '-': '0p',
        '=': '-',
        '[': 'po',
        ']': '[\'',
        '\\': ']',
        ';': 'lk',
        '\'': ';',
        ',': 'm',
        '.': ',',
        '/': '.'
    }

    def __init__(self, driver):
        self.driver = driver

    def wait_for_clickable_element (self, locator, timeout:int=5):
        """
        Waits for an element to become clickable and returns the element.

        Args:
            locator (tuple): The locator of the element to wait for.
            timeout (int, optional): The maximum amount of time to wait in seconds. Defaults to 5.

        Returns:
            WebElement or bool: The clickable element if found, False otherwise.
        """
        try:
            element = WebDriverWait(self.driver, timeout,.5,(TimeoutException)).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except (TimeoutException) as py_ex:
            logging.warning(f'Element not made clickable - timeout - {locator} ')
            return False
    
    def wait_for_element (self, locator, timeout:int=5):
        """
        Waits for the specified element to be visible within the given timeout.

        Args:
            locator (tuple): The locator of the element to wait for.
            timeout (int, optional): The maximum time to wait for the element to be visible, in seconds. Defaults to 5.

        Returns:
            WebElement or False: The element if it is visible within the timeout, False otherwise.
        """
        try:
            element = WebDriverWait(self.driver, timeout,.5,(TimeoutException)).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except (TimeoutException) as py_ex:
            logging.warning(f'Element not found - timeout - {locator} ')
            return False
        
    @staticmethod
    def get_typo(character):
        """
        Returns a random typo for a given character.

        Parameters:
            character (str): The character to generate a typo for.

        Returns:
            str: The generated typo.
        """

        typo = random.choice(
            HumanEmulator.ADJACENT_KEYS.get(character.lower(), '')) 
            
        return typo or character
    
    def key_press(self, key, pause_after):
        """
        Presses a specified key and pauses for a given duration.
        
        Args:
            key (str): The key to be pressed.
            pause_after (float): The duration to pause after the key press.
        
        Returns:
            None
        """
        actions = ActionChains(self.driver)

        (actions.key_down(key)
                .pause(random.uniform(*HumanEmulator.KEY_PRESS_DELAY_RANGE))
                .key_up(key)
                .pause(pause_after)
                .perform()
        )

    def human_type(self, text):
        """
        Generates a human-like typing behavior by emulating typing errors and delays.

        Args:
            text (str): The text to be typed.

        Returns:
            None
        """
        
        actions = ActionChains(self.driver)
        
        for character in text:
            if random.random() < HumanEmulator.TYPO_CHANCE and character.isalpha():
                typo = self.get_typo(character)
                self.key_press(typo, random.uniform(*HumanEmulator.TYPO_CORRECTION_PAUSE_RANGE))
                self.key_press(Keys.BACK_SPACE, random.uniform(*HumanEmulator.TYPING_DELAY_RANGE))
            
            self.key_press(character, random.uniform(*HumanEmulator.TYPING_DELAY_RANGE))


    def human_click(self, locator, timeout:int=5):

        element = self.wait_for_clickable_element(locator)

        if element:
            try:
                size = element.size
            except Exception:
                logging.exception('Element size not found')
                return False
            
            sizeList = list(size.values())
            height = int(sizeList[0])-1
            width = int(sizeList[1])-1

            try:
                height_rand = random.randint(1,height/3) - height/6
            except ValueError:
                height_rand = 0

            try:
                width_rand = random.randint(1,width/3) - width/6
            except ValueError:
                width_rand = 0
            
            retries = 0
                
            while retries < 3:
                
                try:
                    #locate the element again
                    element = self.wait_for_clickable_element(locator)

                    (ActionChains(self.driver)
                        .pause(random.uniform(*HumanEmulator.CLICK_PAUSE_RANGE))
                        .move_to_element_with_offset(element, width_rand, height_rand)
                        .click_and_hold()
                        .pause(random.uniform(*HumanEmulator.CLICK_HOLD_RANGE))
                        .release()
                        .perform()
                    )

                    break

                except StaleElementReferenceException:
                    logging.exception("StaleElementReferenceException with action.perform()")
                    retries += 1
            
            return element