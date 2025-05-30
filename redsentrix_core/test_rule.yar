rule MatchMaliciousPattern
{
    strings:
        $a = "malicious_pattern"
    condition:
        $a
}
