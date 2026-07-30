// cspell:words HINSTANCE STARTUPINFOW ICONERROR
#define UNICODE
#define _UNICODE
#include <windows.h>
#include <filesystem>
#include <string>
#include <vector>

static std::wstring quote(const std::wstring& value) {
    std::wstring result = L"\"";
    unsigned backslashes = 0;
    for (wchar_t character : value) {
        if (character == L'\\') {
            ++backslashes;
        } else {
            if (character == L'"') {
                result.append(backslashes * 2 + 1, L'\\');
            } else {
                result.append(backslashes, L'\\');
            }
            backslashes = 0;
            result.push_back(character);
        }
    }
    result.append(backslashes * 2, L'\\');
    result.push_back(L'"');
    return result;
}

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR arguments, int) {
    std::vector<wchar_t> module(MAX_PATH);
    DWORD length = GetModuleFileNameW(nullptr, module.data(), static_cast<DWORD>(module.size()));
    while (length == module.size() && GetLastError() == ERROR_INSUFFICIENT_BUFFER) {
        module.resize(module.size() * 2);
        length = GetModuleFileNameW(nullptr, module.data(), static_cast<DWORD>(module.size()));
    }
    if (!length) {
        return static_cast<int>(GetLastError());
    }

    const std::filesystem::path root = std::filesystem::path(module.data()).parent_path();
    SetCurrentDirectoryW(root.c_str());
    const auto runtime = root / L"PathOfBuilding-runtime.exe";
    const auto script = root / L"src" / L"Launch.lua";
    std::wstring command = quote(runtime.wstring()) + L" " + quote(script.wstring());
    if (arguments && *arguments) {
        command += L" ";
        command += arguments;
    }
    std::vector<wchar_t> writable(command.begin(), command.end());
    writable.push_back(L'\0');

    STARTUPINFOW startup{sizeof(startup)};
    PROCESS_INFORMATION process{};
    if (!CreateProcessW(
            runtime.c_str(), writable.data(), nullptr, nullptr, FALSE, 0, nullptr,
            root.c_str(), &startup, &process)) {
        const DWORD error = GetLastError();
        MessageBoxW(nullptr, L"Path of Building could not be started.", L"Path of Building", MB_ICONERROR);
        return static_cast<int>(error);
    }
    CloseHandle(process.hThread);
    WaitForSingleObject(process.hProcess, INFINITE);
    DWORD exit_code = 1;
    GetExitCodeProcess(process.hProcess, &exit_code);
    CloseHandle(process.hProcess);
    return static_cast<int>(exit_code);
}
