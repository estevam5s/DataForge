> ⚠️ **DOCUMENTO HISTÓRICO — não reflete a implementação atual.**
>
> Guia de instalação antigo. O atual é `doc/INSTALACAO.md`.
>
> **Documentação vigente:** [`doc/TUTORIAL.md`](TUTORIAL.md) · [`doc/REFERENCIA.md`](REFERENCIA.md) · [`doc/BIBLIOTECA_PADRAO.md`](BIBLIOTECA_PADRAO.md) · [`doc/INSTALACAO.md`](INSTALACAO.md)

---

# 📦 DataForge Installation Guide

This comprehensive guide covers all installation methods for DataForge Programming Language across different platforms and environments.

## 🎯 Quick Install (Windows)

### Method 1: User Installation (Recommended)
Perfect for most users - no administrator privileges required:

```bash
# 1. Clone repository
git clone https://github.com/estevam5s/DataForge.git
cd DataForge

# 2. Install for current user
pip install --user -e .

# 3. Add to PATH (Git Bash/MinGW)
export PATH="$PATH:/c/Users/$USERNAME/AppData/Roaming/Python/Python311/Scripts"

# 4. Make permanent
echo 'export PATH="$PATH:/c/Users/$USERNAME/AppData/Roaming/Python/Python311/Scripts"' >> ~/.bashrc

# 5. Verify installation
dataforge version
```

### Method 2: Direct Python Module
Works immediately without PATH setup:

```bash
# Run directly (always works)
python -m dataforge version
python -m dataforge repl
python -m dataforge run examples/01_hello.df
```

---

## 🖥️ Platform-Specific Instructions

### Windows (PowerShell)
```powershell
# Clone repository
git clone https://github.com/estevam5s/DataForge.git
Set-Location DataForge

# Install for user
pip install --user -e .

# Add to PATH permanently
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$NewPath = "$UserPath;$env:APPDATA\Python\Python311\Scripts"
[Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")

# Restart terminal and test
dataforge version
```

### Windows (Command Prompt)
```cmd
REM Clone repository
git clone https://github.com/estevam5s/DataForge.git
cd DataForge

REM Install for user
pip install --user -e .

REM Add to PATH permanently
setx PATH "%PATH%;%APPDATA%\Python\Python311\Scripts"

REM Restart terminal and test
dataforge version
```

### Linux/macOS (Bash/Zsh)
```bash
# Clone repository
git clone https://github.com/estevam5s/DataForge.git
cd DataForge

# Install for current user
pip install --user -e .

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
dataforge version
```

---

## 🐍 Python Environment Management

### Virtual Environment (Isolated)
```bash
# Create virtual environment
python -m venv dataforge_env

# Activate (Windows)
dataforge_env\Scripts\activate

# Activate (Linux/macOS)  
source dataforge_env/bin/activate

# Install DataForge
pip install -e .

# Verify
dataforge version

# Deactivate when done
deactivate
```

### Conda Environment
```bash
# Create conda environment
conda create -n dataforge python=3.11
conda activate dataforge

# Install DataForge
pip install -e .

# Verify
dataforge version

# Deactivate
conda deactivate
```

### Poetry (Dependency Management)
```bash
# Initialize project
poetry init

# Add DataForge as dependency
poetry add git+https://github.com/estevam5s/DataForge.git

# Install and activate
poetry install
poetry shell

# Run DataForge
dataforge version
```

---

## 🔧 Advanced Installation Options

### Development Installation
For contributors and advanced users:

```bash
# Clone with development tools
git clone https://github.com/estevam5s/DataForge.git
cd DataForge

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests to verify
python -m pytest tests/
```

### Docker Installation
Run DataForge in a containerized environment:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

CMD ["dataforge", "repl"]
```

```bash
# Build and run
docker build -t dataforge .
docker run -it dataforge

# Or run specific file
docker run -v $(pwd):/workspace dataforge run /workspace/program.df
```

### System-Wide Installation
Requires administrator/sudo privileges:

```bash
# Windows (Run as Administrator)
pip install -e .

# Linux/macOS (with sudo)
sudo pip install -e .

# Verify system installation
dataforge version
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Issue: `dataforge: command not found`

**Cause**: Scripts directory not in PATH

**Solutions**:
```bash
# Option 1: Add to PATH temporarily
export PATH="$PATH:/c/Users/$USERNAME/AppData/Roaming/Python/Python311/Scripts"

# Option 2: Use full path
"$APPDATA/Python/Python311/Scripts/dataforge.exe" version

# Option 3: Use Python module
python -m dataforge version

# Option 4: Create alias
alias dataforge="python -m dataforge"
```

#### Issue: `Permission denied` during installation

**Cause**: Insufficient privileges for system directories

**Solutions**:
```bash
# Option 1: User installation (recommended)
pip install --user -e .

# Option 2: Virtual environment
python -m venv venv && source venv/bin/activate
pip install -e .

# Option 3: Run as administrator (Windows)
# Right-click terminal -> "Run as Administrator"
pip install -e .
```

#### Issue: `ModuleNotFoundError: No module named 'dataforge'`

**Cause**: Installation incomplete or Python path issues

**Solutions**:
```bash
# Verify installation
pip list | grep dataforge

# Reinstall if missing
pip install --user -e .

# Check Python path
python -c "import sys; print(sys.path)"

# Force reinstall
pip install --user --force-reinstall -e .
```

#### Issue: `ImportError` or missing dependencies

**Cause**: Missing required Python packages

**Solutions**:
```bash
# Install with dependencies
pip install --user -e .[all]

# Update pip first
python -m pip install --upgrade pip

# Install specific dependencies
pip install setuptools wheel

# Clear cache and reinstall
pip cache purge
pip install --user -e .
```

#### Issue: Version conflicts

**Cause**: Multiple Python versions or conflicting packages

**Solutions**:
```bash
# Check Python version
python --version  # Should be 3.10+

# Use specific Python version
python3.11 -m pip install --user -e .

# Create isolated environment
python -m venv clean_env
source clean_env/bin/activate  # Linux/macOS
# or clean_env\Scripts\activate  # Windows
pip install -e .
```

---

## 🛠️ Configuration

### Environment Variables
```bash
# Optional: Set DataForge home directory
export DATAFORGE_HOME="/path/to/dataforge"

# Optional: Set debug mode
export DATAFORGE_DEBUG=1

# Optional: Custom library path
export DATAFORGE_LIB_PATH="/custom/lib/path"
```

### Configuration File
Create `~/.dataforge/config.toml`:

```toml
[general]
debug = false
color_output = true

[paths]
lib_path = "~/.dataforge/lib"
cache_dir = "~/.dataforge/cache"

[editor]
default_editor = "code"
syntax_highlighting = true

[repl]
history_size = 1000
auto_indent = true
```

---

## ✅ Verification Checklist

After installation, verify everything works:

```bash
# 1. Check version
dataforge version
# Expected: DataForge v3.0.0

# 2. Test help command
dataforge --help
# Expected: Usage and command list

# 3. Run hello world
dataforge run examples/01_hello.df
# Expected: "Hello, World!" output

# 4. Test REPL
echo 'out "Hello from REPL!"' | dataforge repl
# Expected: Interactive session output

# 5. Check Python module
python -m dataforge version
# Expected: Same version output

# 6. Verify standard library
python -c "from dataforge.stdlib import arcane_math; print('✓ Standard library OK')"
# Expected: "✓ Standard library OK"
```

---

## 🔄 Updating DataForge

### From Git Repository
```bash
# Navigate to DataForge directory
cd DataForge

# Pull latest changes
git pull origin main

# Reinstall if needed
pip install --user -e .

# Verify new version
dataforge version
```

### Development Builds
```bash
# Switch to development branch
git checkout develop
git pull origin develop

# Install development version
pip install --user -e .

# Run development tests
python -m pytest tests/
```

---

## 🗑️ Uninstallation

### Remove DataForge
```bash
# Uninstall package
pip uninstall dataforge-lang

# Remove from PATH (manual)
# Edit ~/.bashrc and remove DataForge PATH entries

# Clean up directories
rm -rf ~/.dataforge  # Configuration
rm -rf DataForge/     # Source code (if cloned)
```

### Complete Cleanup
```bash
# Remove all traces
pip uninstall dataforge-lang
rm -rf ~/.dataforge
rm -rf ~/.cache/dataforge
# Remove PATH entries from shell config files
```

---

## 📞 Support

If you encounter issues not covered here:

1. **Check Issues**: [GitHub Issues](https://github.com/estevam5s/DataForge/issues)
2. **Search Documentation**: [DataForge Docs](https://docs.dataforge-lang.org)
3. **Community Help**: [Discussions](https://github.com/estevam5s/DataForge/discussions)
4. **Report Bug**: Create new issue with installation details

### Include in Bug Reports
- Operating system and version
- Python version (`python --version`)
- Installation method used
- Complete error message
- Steps to reproduce

---

**Happy coding with DataForge! 🚀**