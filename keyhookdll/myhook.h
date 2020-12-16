#pragma once
#include <Windows.h>
#include <tchar.h>

#ifdef KEYHOOKDLL_EXPORTS
#define KEYHOOKDLL_API __declspec(dllexport)
#else
#define KEYHOOKDLL_API __declspec(dllimport)
#endif

#define UWM_KBHOOK_MSG _T("UMW_KBHOOK-{B30856F0-D3DD-11d4-A00B-006067718D04}")

extern "C" KEYHOOKDLL_API BOOL WINAPI setMyHook(HWND hWnd);

extern "C" KEYHOOKDLL_API BOOL clearMyHook(HWND hWnd);

extern "C" KEYHOOKDLL_API LPCSTR message_string();