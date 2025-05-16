rule DummyTestRule
{
    meta:
        description = "Detects the test string in memory"
        author = "RedSentrix"
    strings:
        $a = "ThisIsATestString"
    condition:
        $a
}
