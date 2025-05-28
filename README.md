# Flask File Manager

A secure web-based file management system built with Flask that allows users to upload, download, organize, and manage their files through a web interface.

## Features

### User Management
- User registration and authentication
- Secure password hashing
- Session-based login system
- Individual user storage directories

### File Operations
- **Upload**: Upload files up to 16MB
- **Download**: Download files securely
- **Create Folders**: Organize files in custom directories
- **Rename**: Rename files and folders
- **Delete**: Remove files and folders
- **Copy/Cut/Paste**: Move and duplicate files between directories
- **Navigation**: Browse through folder structures

### Security Features
- Path traversal protection
- Secure filename handling
- User-isolated storage
- Session management
- Access control validation

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Werkzeug password hashing
- **File Handling**: Python os, shutil modules
- **Frontend**: HTML templates (Jinja2)

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flask-file-manager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy werkzeug
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
flask-file-manager/
├── app.py                 # Main Flask application
├── templates/             # HTML templates directory
│   ├── login.html        # Login page template
│   ├── register.html     # Registration page template
│   └── file_manager.html # File manager interface template
├── storage/              # User files storage directory (auto-created)
│   └── [username]/       # Individual user directories
├── users.db              # SQLite database (auto-created)
└── README.md            # This file
```

## Frontend Templates Required

The application expects the following HTML templates in the `templates/` directory:

### 1. `login.html`
Login page with form fields:
```html
<!-- Expected form fields -->
<form method="POST">
    <input type="text" name="username" required>
    <input type="password" name="password" required>
    <button type="submit">Login</button>
</form>
<a href="/register">Register</a>
```

### 2. `register.html`
Registration page with form fields:
```html
<!-- Expected form fields -->
<form method="POST">
    <input type="text" name="username" required>
    <input type="password" name="password" required>
    <button type="submit">Register</button>
</form>
<a href="/login">Back to Login</a>
```

### 3. `file_manager.html`
Main file management interface that should handle:
```html
<!-- File upload form -->
<form method="POST" action="/upload" enctype="multipart/form-data">
    <input type="file" name="file" required>
    <input type="hidden" name="current_dir" value="{{ current_dir }}">
    <button type="submit">Upload</button>
</form>

<!-- Create folder form -->
<form method="POST" action="/create_folder">
    <input type="text" name="folder_name" required>
    <input type="hidden" name="current_dir" value="{{ current_dir }}">
    <button type="submit">Create Folder</button>
</form>

<!-- Display files and folders with operations -->
<!-- Files: {{ files }}, Folders: {{ folders }} -->
<!-- Current directory: {{ current_dir }} -->
<!-- Parent directory: {{ parent_dir }} -->
<!-- Username: {{ username }} -->
```

## API Endpoints

### Authentication Routes
- `GET /` - Home page (redirects to login if not authenticated)
- `GET, POST /login` - User login
- `GET, POST /register` - User registration
- `GET /logout` - User logout

### File Management Routes
- `GET /file_manager` - Main file manager interface
- `POST /upload` - Upload files
- `GET /download` - Download files
- `POST /create_folder` - Create new folders
- `POST /rename` - Rename files/folders
- `POST /delete` - Delete files/folders
- `POST /copy` - Mark items for copying
- `POST /cut` - Mark items for moving
- `POST /paste` - Paste copied/cut items

## Configuration

## Security Considerations

### Current Security Measures
- Password hashing with Werkzeug
- Path traversal protection
- Secure filename handling
- User-isolated storage directories
- Session-based authentication

### Production Recommendations
1. **Change the SECRET_KEY**: Use a strong, random secret key
2. **Use HTTPS**: Enable SSL/TLS in production
3. **Database Security**: Use PostgreSQL or MySQL instead of SQLite
4. **Environment Variables**: Store sensitive config in environment variables
5. **File Type Validation**: Add file type restrictions if needed
6. **Rate Limiting**: Implement upload rate limiting
7. **Virus Scanning**: Add malware scanning for uploaded files

## Development

### Running in Development Mode
```bash
python app.py
```
The application runs on `http://localhost:5000` with debug mode enabled.

### Database Initialization
The database and storage directories are automatically created on first run.

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure the application has write permissions for the storage directory
2. **Database Errors**: Check if the SQLite database file is writable
3. **Upload Failures**: Verify file size is under 16MB limit
4. **Template Errors**: Ensure all required templates exist in the templates directory

### Logs
Check the Flask development server output for error messages and debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Frontend Integration

To create a complete file management system, you'll need to implement the HTML templates mentioned above. Consider using:

- **Bootstrap** or **Tailwind CSS** for responsive design
- **JavaScript** for dynamic file operations and AJAX requests
- **Font Awesome** or similar for file type icons
- **Progress bars** for upload status
- **Modal dialogs** for confirmations

### Sample Frontend Features
- Drag and drop file uploads
- File preview thumbnails
- Breadcrumb navigation
- Context menus for file operations
- Progress indicators
- Responsive design for mobile devices

## Support

If you encounter any issues or have questions, please create an issue in the repository or contact the development team.
