// dllmain.cpp : Defines the entry point for the DLL application.
#include "pch.h"
#include "myhook.h"

#pragma data_seg(".KBH")
HWND hWndServer = NULL;
#pragma data_seg()
#pragma comment(linker, "/section:.KBH,rws")

HINSTANCE hInstance;
UINT UWM_KBHOOK;
HHOOK hook;

static LRESULT CALLBACK msghook(int nCode, WPARAM wParam, LPARAM lParam);

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        hInstance = (HINSTANCE)hModule;
        UWM_KBHOOK = RegisterWindowMessage(UWM_KBHOOK_MSG);
        return TRUE;
    case DLL_PROCESS_DETACH:
        if (hWndServer != NULL)
            clearMyHook(hWndServer);
        return TRUE;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
        break;
    }
    return TRUE;
}

extern "C" KEYHOOKDLL_API BOOL WINAPI setMyHook(HWND hWnd) {
    if (hWndServer != NULL)
        return FALSE;

    hook = SetWindowsHookEx(
        WH_KEYBOARD,
        (HOOKPROC)msghook,
        hInstance,
        0
    );

    if (hook != NULL) {
        hWndServer = hWnd;
        return TRUE;
    }
    return FALSE;
}

extern "C" KEYHOOKDLL_API BOOL clearMyHook(HWND hWnd) {
    if (hWnd != hWndServer)
        return FALSE;
    BOOL unhooked = UnhookWindowsHookEx(hook);
    if (unhooked)
        hWndServer = NULL;
    return unhooked;
}

static LRESULT CALLBACK msghook(int nCode, WPARAM wParam, LPARAM lParam) {
    if (SendMessage(hWndServer, UWM_KBHOOK, wParam, lParam)) 
        return 1;
    return CallNextHookEx(hook, nCode, wParam, lParam);
}

extern "C" KEYHOOKDLL_API LPCSTR message_string() {
    return (LPCSTR)UWM_KBHOOK_MSG;
}