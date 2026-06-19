"""
AutoCrack GUI - Archive Password Recovery Application
Main entry point
"""
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autocrack.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("AutoCrack GUI")
        app.setApplicationVersion("1.0.0")
        
        logger.info("=" * 60)
        logger.info("AutoCrack GUI - Archive Password Recovery")
        logger.info("=" * 60)
        
        # Import after QApplication creation
        from gui.main_window import MainWindow
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
