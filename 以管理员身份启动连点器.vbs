Set shellApp = CreateObject("Shell.Application")
Set fileSystem = CreateObject("Scripting.FileSystemObject")
Set wshShell = CreateObject("WScript.Shell")

scriptDir = fileSystem.GetParentFolderName(WScript.ScriptFullName)
pythonwPath = wshShell.ExpandEnvironmentStrings("%SystemDrive%\Python314\pythonw.exe")

If Not fileSystem.FileExists(pythonwPath) Then
    pythonwPath = "pythonw.exe"
End If

arguments = Chr(34) & fileSystem.BuildPath(scriptDir, "main.py") & Chr(34)
shellApp.ShellExecute pythonwPath, arguments, scriptDir, "runas", 0
