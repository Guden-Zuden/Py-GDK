import time as _time
import colorama

__all__ = ["Log"]

colorama.init(True)

# def _colorPrint(text: str, color: int, isBold: bool = False):
#     """0: Black\n
#     1: Red\n
#     2: Green\n
#     3: Yellow\n
#     4: Blue\n
#     5: Magenta\n
#     6: Cyan\n
#     7: White"""
#     if isBold: print("\033[1m", end = "")

#     if   color == 0: print("\033[30m", end = "")
#     elif color == 1: print("\033[31m", end = "")
#     elif color == 2: print("\033[32m", end = "")
#     elif color == 3: print("\033[33m", end = "")
#     elif color == 4: print("\033[34m", end = "")
#     elif color == 5: print("\033[35m", end = "")
#     elif color == 6: print("\033[36m", end = "")
#     elif color == 7: print("\033[37m", end = "")

#     print(text, end = "")

#     print("\033[0m") # Reset Color

class Log:
    log_level: int = 0
    """log level\n
    Info: 0 Warn: 1 Error: 2 Critical Error: 3"""

    @staticmethod
    def _get_time():
        time = _time.ctime().split()
        return " ".join(time[:-1])

    @staticmethod
    def info(title: str, message: str):
        if Log.log_level < 0: return
        print(f"{{{Log._get_time()}}} [INFO] [{title}]: {message}")
        
    @staticmethod
    def warn(title: str, message: str):
        if Log.log_level < 0: return
        print(colorama.Fore.YELLOW + f"{{{Log._get_time()}}} [WARN] [{title}]: {message}" + colorama.Fore.RESET)

    @staticmethod
    def error(title: str, message: str):
        if Log.log_level < 0: return
        print(colorama.Fore.RED + f"{{{Log._get_time()}}} [ERROR] [{title}]: {message}" + colorama.Fore.RESET)
        raise Exception(f"{{{Log._get_time()}}} [ERROR] [{title}]: {message}")

    @staticmethod
    def critical(title: str, message: str):
        if Log.log_level < 0: return
        print(colorama.Style.BRIGHT + colorama.Back.RED + f"{{{Log._get_time()}}} [**CRITICAL**] [{title}]: {message}" + colorama.Style.RESET_ALL + colorama.Fore.RESET)
        raise Exception(f"{{{Log._get_time()}}} [**CRITICAL**] [{title}]: {message}")
