# Security Policy

## "Deflatpak" and Sandboxing

**Bottles Deflatpak is Native by default.**

Unlike the official Bottles release which is forced into a Flatpak container, this version runs natively. However, it includes an **optional native sandbox** powered by `bubblewrap`.

### Security Modes

1.  **Native Mode (Default)**: Window programs run with your full user permissions. They can read/write any file you own.
2.  **Dedicated Sandbox (Optional)**: Can be enabled per-bottle. This uses `bubblewrap` to:
    -   Provide a read-only view of the host root.
    -   Isolate the network (optional).
    -   Limit access to specific paths.
    -   *Note: GPU passthrough and PulseAudio are shared to ensure functionality.*

### Implications of Native Execution

1.  **System Integration**: Relies on system libraries (glibc, python, etc.). Vulnerabilities in your system affect the application.
2.  **User Data**: Without the sandbox enabled, malware can access your entire `$HOME` directory.

### User Responsibility

By using this native version, **you acknowledge that you are running Windows executables directly on your host system**.

-   Only run software from trusted sources.
-   Be aware that "ransomware" or malware running inside this version of Bottles can encrypt or destroy your personal files on the Linux host.

## Reporting Vulnerabilities

If you find a vulnerability specific to the *packaging* or *deflatpak modifications* of this project, please open an issue on the [GitHub Repository](https://github.com/tenshou170/Bottles-Deflatpak/issues).

For vulnerabilities in the core Bottles logic or Windows runners, please refer to the upstream [Bottles Security Policy](https://github.com/bottlesdevs/Bottles/security/policy).
