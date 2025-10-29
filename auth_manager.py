import keyring
import logging

# A unique service name for our application to store credentials under.
SERVICE_NAME = "ChronoAI"

class AuthManager:
    """
    Manages secure storage and retrieval of API tokens using the OS
    native credential manager (e.g., Windows Credential Manager, macOS Keychain).

    This class provides a static interface, so it doesn't need to be instantiated.
    This directly addresses the NFR-Security requirement from the PRD.
    """

    @staticmethod
    def save_token(account_name: str, token: str):
        """
        Saves a token for a specific account (e.g., 'google' or 'zoho').

        Args:
            account_name (str): The name of the account/service (e.g., 'google').
            token (str): The token (e.g., refresh token) to be stored securely.
        """
        try:
            keyring.set_password(SERVICE_NAME, account_name, token)
            logging.info(f"Successfully saved token for '{account_name}'.")
        except Exception as e:
            logging.error(f"Failed to save token for '{account_name}': {e}")

    @staticmethod
    def get_token(account_name: str) -> str | None:
        """
        Retrieves a token for a specific account.

        Args:
            account_name (str): The name of the account/service (e.g., 'google').

        Returns:
            str | None: The retrieved token, or None if not found or an error occurs.
        """
        try:
            token = keyring.get_password(SERVICE_NAME, account_name)
            if token:
                logging.info(f"Successfully retrieved token for '{account_name}'.")
            else:
                logging.info(f"No token found for '{account_name}'.")
            return token
        except Exception as e:
            logging.error(f"Failed to retrieve token for '{account_name}': {e}")
            return None

    @staticmethod
    def delete_token(account_name: str):
        """
        Deletes a token for a specific account from the credential store.

        Args:
            account_name (str): The name of the account/service (e.g., 'google').
        """
        try:
            # Use get_password to check existence before trying to delete
            if keyring.get_password(SERVICE_NAME, account_name) is not None:
                keyring.delete_password(SERVICE_NAME, account_name)
                logging.info(f"Successfully deleted token for '{account_name}'.")
            else:
                logging.warning(f"Attempted to delete non-existent token for '{account_name}'.")
        except Exception as e:
            logging.error(f"An error occurred while deleting token for '{account_name}': {e}")