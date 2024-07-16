import win32api, win32con, win32gui, win32ui

text_to_display = ""
class_registered = False
className = 'MyWindowClassName'
hInstance = win32api.GetModuleHandle()
hWindow = None

def display(text):
    global text_to_display, class_registered, hWindow
    text_to_display = text

    if not class_registered:
        wndClass = win32gui.WNDCLASS()
        wndClass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wndClass.lpfnWndProc = wndProc
        wndClass.hInstance = hInstance
        wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        wndClass.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        wndClass.lpszClassName = className
        win32gui.RegisterClass(wndClass)
        class_registered = True

    if not hWindow:
        exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
        style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

        hWindow = win32gui.CreateWindowEx(
            exStyle,
            className,
            None,
            style,
            0,
            0,
            win32api.GetSystemMetrics(win32con.SM_CXSCREEN),
            win32api.GetSystemMetrics(win32con.SM_CYSCREEN),
            None,
            None,
            hInstance,
            None
        )

        win32gui.SetLayeredWindowAttributes(hWindow, 0x00ffffff, 255, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
        win32gui.SetWindowPos(hWindow, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
    
    win32gui.InvalidateRect(hWindow, None, True)
    win32gui.UpdateWindow(hWindow)

def clear_screen():
    global text_to_display
    text_to_display = ""
    if hWindow:
        win32gui.InvalidateRect(hWindow, None, True)
        win32gui.UpdateWindow(hWindow)

def wndProc(hWnd, message, wParam, lParam):
    if message == win32con.WM_PAINT:
        hdc, paintStruct = win32gui.BeginPaint(hWnd)

        dpiScale = win32ui.GetDeviceCaps(hdc, win32con.LOGPIXELSX) / 60.0
        fontSize = 120

        lf = win32gui.LOGFONT()
        lf.lfFaceName = "Arial Black"
        lf.lfHeight = int(round(dpiScale * fontSize))
        hf = win32gui.CreateFontIndirect(lf)
        win32gui.SelectObject(hdc, hf)

        win32gui.SetTextColor(hdc, win32api.RGB(255, 255, 254))

        rect = win32gui.GetClientRect(hWnd)
        screen_height = rect[3]
        lower_third_top = int(screen_height * 2 / 3)
        rect = (rect[0], lower_third_top, rect[2], screen_height)

        win32gui.DrawText(
            hdc,
            text_to_display,
            -1,
            rect,
            win32con.DT_CENTER | win32con.DT_NOCLIP | win32con.DT_SINGLELINE | win32con.DT_VCENTER
        )
        win32gui.EndPaint(hWnd, paintStruct)
        return 0

    elif message == win32con.WM_TIMER:
        win32gui.InvalidateRect(hWnd, None, True)
        return 0

    elif message == win32con.WM_DESTROY:
        win32gui.PostQuitMessage(0)
        return 0

    else:
        return win32gui.DefWindowProc(hWnd, message, wParam, lParam)
