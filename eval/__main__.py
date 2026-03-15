"""Allow running eval as a package: python3 -m eval"""
import sys

from .cli import main

sys.exit(main())
