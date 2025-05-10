rule SuspiciousAPI {
    meta:
        description = "Detects suspicious Windows API calls"
    strings:
        $a1 = "CreateRemoteThread"
        $a2 = "WinExec"
        $a3 = "VirtualAlloc"
    condition:
        any of them
}

rule EICARTest {
    meta:
        description = "EICAR antivirus test string"
    strings:
        $e = "X5O!P%@AP[4\\\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    condition:
        $e
}
