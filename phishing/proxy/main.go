package main

import (
	"flag"
	"fmt"
	"log"
	"os"

	"redsentrix-phishing/proxy"
	"redsentrix-phishing/certs"
)

func main() {
	var (
		port      = flag.Int("port", 8080, "Proxy port")
		target    = flag.String("target", "", "Target URL to proxy")
		certPath  = flag.String("cert", "", "Certificate file path")
		keyPath   = flag.String("key", "", "Private key file path")
		domain    = flag.String("domain", "localhost", "Domain for certificate generation")
		genCert   = flag.Bool("gen-cert", false, "Generate self-signed certificate")
	)
	flag.Parse()

	// Generate certificate if requested
	if *genCert {
		certFile := "build/phishing/cert.pem"
		keyFile := "build/phishing/key.pem"
		
		os.MkdirAll("build/phishing", 0755)
		
		if err := certs.GenerateCertificate(*domain, certFile, keyFile); err != nil {
			log.Fatalf("Failed to generate certificate: %v", err)
		}
		
		log.Printf("Certificate generated: %s, %s", certFile, keyFile)
		*certPath = certFile
		*keyPath = keyFile
	}

	if *target == "" {
		log.Fatal("Target URL is required (-target)")
	}

	// Create and start proxy server
	proxyServer := proxy.NewProxyServer(*port, *target, *certPath, *keyPath)
	
	log.Printf("Starting RedSentrix phishing proxy...")
	log.Printf("Target: %s", *target)
	log.Printf("Port: %d", *port)
	
	if err := proxyServer.Start(); err != nil {
		log.Fatalf("Proxy server error: %v", err)
	}
}

