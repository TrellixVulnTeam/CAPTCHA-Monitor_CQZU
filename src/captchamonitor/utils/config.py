import os
import sys
import logging

ENV_VARS = {
    "db_host": "CM_DB_HOST",
    "db_port": "CM_DB_PORT",
    "db_name": "CM_DB_NAME",
    "db_user": "CM_DB_USER",
    "db_password": "CM_DB_PASSWORD",
}


class Config:
    """
    Behaves like a real python dictionary and also reads config variables from
    the environment

    Based on: https://gist.github.com/turicas/1510860
    """

    def __init__(self, init=None):
        self.logger = logging.getLogger(__name__)

        # Add if initial values are passed
        if init is not None:
            self.__dict__.update(init)

        # Read environment variables
        for key, value in ENV_VARS.items():
            self.__dict__[key] = os.environ.get(value, None)
            if self.__dict__[key] is None:
                self.logger.error("Missing configuration variable: %s", value)
                self.exit()

    def exit(self):
        self.logger.error("Exitting!")
        sys.exit(1)

    def __getitem__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            self.logger.error("Requested key doesn't exist in config: %s", key)
            self.exit()

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)
