# Application details
APP_NAME = "@APP_NAME@"
if APP_NAME == "@APP_NAME@":
    APP_NAME = "Bottles"

APP_NAME_LOWER = APP_NAME.lower()

BASE_ID = "@BASE_ID@"
if BASE_ID == "@BASE_ID@":
    BASE_ID = "com.usebottles.bottles"

APP_ID = "@APP_ID@"
if APP_ID == "@APP_ID@":
    APP_ID = BASE_ID

APP_VERSION = "@APP_VERSION@"
if APP_VERSION == "@APP_VERSION@":
    APP_VERSION = "60.1"

APP_MAJOR_VERSION = "@APP_MAJOR_VERSION@"
if APP_MAJOR_VERSION == "@APP_MAJOR_VERSION@":
    APP_MAJOR_VERSION = "60"

APP_MINOR_VERSION = "@APP_MINOR_VERSION@"
if APP_MINOR_VERSION == "@APP_MINOR_VERSION@":
    APP_MINOR_VERSION = "1"

APP_ICON = APP_ID
PROFILE = "@PROFILE@"
if PROFILE == "@PROFILE@":
    PROFILE = "default"

# Internal settings not user editable
ANIM_DURATION = 120

# General purpose definitions
EXECUTABLE_EXTS = (".exe", ".msi", ".bat", ".lnk")

# URLs
DOC_URL = "https://docs.usebottles.com"
