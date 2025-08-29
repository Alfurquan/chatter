# Logging System - Factory Pattern with Hierarchical Logging

This directory implements a production-ready logging system using the Factory Pattern combined with Python's hierarchical logging capabilities. This design is commonly used in distributed systems.

## 🏗️ Architecture Overview

### Core Components
1. **Factory Pattern** - Creates different logger types
2. **Hierarchical Logging** - Parent-child logger relationships
3. **Single Setup** - Configure once, use everywhere
4. **Consistent Interface** - Same API across all modules

## 📁 File Structure

```
app/logging/
├── __init__.py           # Public API exports
├── base.py              # Abstract base logger interface
├── factory.py           # Logger factory implementation
├── formatters.py        # JSON and Standard formatters
├── json_logger.py       # JSON logger implementation
├── standard.py          # Standard logger implementation
└── README.md           # This documentation
```

## 🎯 How It Works

### Step 1: Single Setup (Once in main.py)
```python
# coordinator/main.py
from app.logging import LoggerFactory

# Set up logging once for the entire application
LoggerFactory.create_logger("coordinator", "json")
```

**What happens:**
1. Factory creates JsonLogger instance with name "coordinator"
2. Calls `setup()` which configures Python's logging system
3. Adds handler (console output) and formatter (JSON) to "coordinator" logger

### Step 2: Hierarchical Usage (Everywhere else)
```python
# coordinator/api/routes.py
import logging
logger = logging.getLogger("coordinator.routes")

# coordinator/core/cluster_manager.py
import logging
logger = logging.getLogger("coordinator.cluster")

# coordinator/nodes/registry.py
import logging
logger = logging.getLogger("coordinator.registry")
```

**What happens:**
1. Python recognizes `"coordinator.routes"` as child of `"coordinator"`
2. Child loggers **automatically inherit** parent's configuration:
   - ✅ Handlers (console output)
   - ✅ Formatters (JSON format)
   - ✅ Log levels
3. No additional setup needed!

## 🧠 Key Concepts

### Python Logging Hierarchy
```
coordinator                    ← Parent (configured once)
├── coordinator.routes         ← Child (inherits config)
├── coordinator.cluster        ← Child (inherits config)
└── coordinator.registry       ← Child (inherits config)
```

- **Dot notation** creates parent-child relationships
- **Children inherit** parent configuration automatically
- **One setup** affects entire hierarchy

### Factory Pattern Benefits
- **Centralized Creation**: All logger creation in one place
- **Type Safety**: Consistent interface across implementations
- **Easy Extension**: Add new logger types without changing existing code
- **Configuration**: Single place to change logger behavior

## 📋 Component Details

### 1. BaseLogger (base.py)
```python
class BaseLogger(ABC):
    @abstractmethod
    def setup(self) -> logging.Logger:
        pass
```
- **Purpose**: Ensures all logger implementations have consistent interface
- **Pattern**: Abstract Factory + Template Method
- **Benefit**: Can swap logger types without changing client code

### 2. Concrete Implementations
- **JsonLogger** - Formats logs as JSON objects
- **StandardLogger** - Formats logs as text
- **Pattern**: Strategy Pattern (different formatting behaviors)
- **Key**: Both inherit same interface, different implementations

### 3. Factory Class (factory.py)
```python
@classmethod
def create_logger(cls, name: str, logger_type: str = "standard") -> BaseLogger:
    if logger_type == "json":
        logger_instance = JsonLogger(name)
    elif logger_type == "standard":
        logger_instance = StandardLogger(name)
    else:
        raise ValueError(f"Unknown logger type: {logger_type}")
    
    # Actually set up the logger
    logger_instance.setup()  # ← Critical: Configures Python's logging system
    return logger_instance
```
- **Purpose**: Centralized logger creation
- **Pattern**: Factory Method Pattern
- **Key**: `setup()` call actually configures Python's logging system

### 4. Formatters (formatters.py)
- **StandardFormatter**: Uses configured text format from config
- **JsonFormatter**: Outputs structured JSON with timestamp, level, message, logger name

## 🚀 Usage Examples

### Basic Usage
```python
# In main.py (setup once)
from app.logging import LoggerFactory
LoggerFactory.create_logger("coordinator", "json")

# In any module (use everywhere)
import logging
logger = logging.getLogger("coordinator.routes")
logger.info("Processing request", extra={"key": "value"})
```

### Different Logger Types
```python
# JSON output
LoggerFactory.create_logger("coordinator", "json")

# Standard text output
LoggerFactory.create_logger("coordinator", "standard")
```

### Environment-Based Configuration
```python
import os
logger_type = os.environ.get("LOG_FORMAT", "standard")
LoggerFactory.create_logger("coordinator", logger_type)
```

## 📚 Design Patterns Used

### 1. Factory Method Pattern
```python
LoggerFactory.create_logger(name, type)  # Creates appropriate logger type
```

### 2. Strategy Pattern
```python
JsonFormatter vs StandardFormatter  # Different formatting strategies
```

### 3. Template Method Pattern
```python
BaseLogger.setup()  # Defines the setup algorithm, subclasses implement details
```

### 4. Dependency Injection
```python
# Each module gets its logger, doesn't create it
logger = logging.getLogger("coordinator.routes")
```

## 🎯 System Design

### Scalability Questions
- **"How would you handle millions of log messages?"** 
  - Answer: Async handlers, buffering, log shipping
- **"How would you add new log destinations?"** 
  - Answer: Add new handlers to parent logger
- **"How would you handle different environments?"** 
  - Answer: Environment-based factory configuration

### Design Questions
- **"Why factory pattern?"** 
  - Answer: Centralized creation, easy to extend, type safety
- **"Why hierarchical logging?"** 
  - Answer: Single configuration, module identification, inheritance
- **"Why not global singleton?"** 
  - Answer: Testing difficulties, hidden dependencies

## 🔧 Complete Flow

### Initialization (Once)
```python
# main.py
LoggerFactory.create_logger("coordinator", "json")
```
1. Factory creates JsonLogger("coordinator")
2. JsonLogger.setup() configures Python's logging system
3. Adds StreamHandler with JsonFormatter to "coordinator" logger

### Usage (Everywhere)
```python
# Any module
logger = logging.getLogger("coordinator.module_name")
logger.info("Test message")
```
1. Gets child logger of "coordinator"
2. Inherits parent's handler and formatter
3. Outputs JSON to console automatically

## 💡 Why This Design is Powerful

### ✅ Single Responsibility Principle
- Factory: Creates loggers
- Formatters: Format output
- Loggers: Handle logging logic

### ✅ Open/Closed Principle
- Easy to add new logger types
- Existing code doesn't change

### ✅ Dependency Inversion Principle
- Modules depend on logging interface, not concrete implementations
- Can mock easily for testing

### ✅ Configuration Management
- One place to change logging behavior
- Environment-specific configurations possible

## 🧪 Testing

### Unit Testing
```python
# Mock the factory for testing
def test_logging():
    # Can easily mock LoggerFactory.create_logger()
    pass
```

### Integration Testing
```python
# Test different logger types
def test_json_logger():
    logger = LoggerFactory.create_logger("test", "json")
    # Test JSON output format
    
def test_standard_logger():
    logger = LoggerFactory.create_logger("test", "standard")
    # Test standard output format
```

## 🔮 Future Enhancements

1. **Async Logging**: Add async handlers for high-throughput scenarios
2. **Log Shipping**: Add handlers for external log aggregation systems
3. **Metrics Integration**: Add metrics collection to formatters
4. **Circuit Breakers**: Add fault tolerance for external logging systems
5. **Configuration Hot-Reload**: Support runtime configuration changes

This logging system is production-ready and follows industry best practices for distributed systems.
