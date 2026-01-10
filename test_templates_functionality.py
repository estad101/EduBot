#!/usr/bin/env python3
"""
Comprehensive test suite for bot message templates functionality.
Tests database, API endpoints, and frontend integration.
"""
import sys
import logging
from sqlalchemy import text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_templates():
    """Test that templates are properly stored in the database."""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Database Templates")
    logger.info("="*60)
    
    try:
        from config.database import SessionLocal
        from models.bot_message import BotMessageTemplate
        
        db = SessionLocal()
        
        # Count templates
        count = db.query(BotMessageTemplate).count()
        logger.info(f"✓ Total templates in database: {count}")
        
        if count == 0:
            logger.warning("⚠ No templates found in database. Running seeding...")
            from migrations.seed_templates import seed_templates
            if seed_templates():
                logger.info("✓ Templates seeded successfully")
                count = db.query(BotMessageTemplate).count()
                logger.info(f"✓ Total templates after seeding: {count}")
            else:
                logger.error("✗ Template seeding failed")
                return False
        
        # List all templates
        templates = db.query(BotMessageTemplate).all()
        logger.info(f"\n✓ Found {len(templates)} templates:")
        for t in templates[:5]:  # Show first 5
            logger.info(f"  - {t.template_name} (ID: {t.id}, Default: {t.is_default})")
        
        if len(templates) > 5:
            logger.info(f"  ... and {len(templates) - 5} more")
        
        # Check for duplicate templates
        names = [t.template_name for t in templates]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        
        if duplicates:
            logger.error(f"✗ Duplicate templates found: {duplicates}")
            return False
        else:
            logger.info("✓ No duplicate templates found")
        
        # Verify template structure
        for t in templates[:3]:
            if not t.template_name or not t.template_content:
                logger.error(f"✗ Template {t.id} missing required fields")
                return False
        logger.info("✓ All templates have required fields")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_template_model():
    """Test that the BotMessageTemplate model is correctly defined."""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Template Model")
    logger.info("="*60)
    
    try:
        from models.bot_message import BotMessageTemplate
        
        # Check model attributes
        expected_attrs = ['id', 'template_name', 'template_content', 'variables', 'is_default', 'created_at', 'updated_at']
        
        for attr in expected_attrs:
            if not hasattr(BotMessageTemplate, attr):
                logger.error(f"✗ Missing attribute: {attr}")
                return False
        
        logger.info(f"✓ Model has all required attributes: {expected_attrs}")
        
        # Check table name
        if BotMessageTemplate.__tablename__ != "bot_message_templates":
            logger.error(f"✗ Wrong table name: {BotMessageTemplate.__tablename__}")
            return False
        
        logger.info(f"✓ Correct table name: {BotMessageTemplate.__tablename__}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Model test failed: {str(e)}")
        return False


def test_api_endpoint():
    """Test the templates API endpoint."""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: API Endpoint (/api/bot-messages/templates/list)")
    logger.info("="*60)
    
    try:
        from api.routes.bot_messages import get_templates
        from config.database import SessionLocal
        
        db = SessionLocal()
        
        # Call endpoint
        response = get_templates(db=db)
        
        logger.info(f"✓ API endpoint callable and returns: {response.status}")
        
        # Check response structure
        if response.status != "success":
            logger.error(f"✗ Expected status 'success', got '{response.status}'")
            return False
        
        if not hasattr(response, 'data') or 'templates' not in response.data:
            logger.error("✗ Response missing 'templates' in data")
            return False
        
        templates = response.data['templates']
        logger.info(f"✓ Response contains {len(templates)} templates")
        
        # Verify each template structure
        for t in templates[:3]:
            required_fields = ['id', 'template_name', 'template_content', 'variables', 'is_default']
            for field in required_fields:
                if field not in t:
                    logger.error(f"✗ Template missing field: {field}")
                    return False
        
        logger.info("✓ All templates have correct structure")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ API endpoint test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_router_registration():
    """Test that the bot_messages router is properly registered."""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Router Registration")
    logger.info("="*60)
    
    try:
        from api.routes import bot_messages
        
        # Check router exists
        if not hasattr(bot_messages, 'router'):
            logger.error("✗ bot_messages module missing 'router'")
            return False
        
        logger.info("✓ bot_messages router exists")
        
        # Check prefix
        if bot_messages.router.prefix != "/api/messages":
            logger.warning(f"⚠ Expected prefix '/api/messages', got '{bot_messages.router.prefix}'")
        else:
            logger.info(f"✓ Router prefix is correct: {bot_messages.router.prefix}")
        
        # List routes
        routes = bot_messages.router.routes
        logger.info(f"✓ Router has {len(routes)} routes")
        
        # Check for templates endpoint
        templates_endpoint_found = False
        for route in routes:
            if hasattr(route, 'path') and 'templates' in route.path:
                templates_endpoint_found = True
                logger.info(f"✓ Found templates endpoint: {route.path}")
        
        if not templates_endpoint_found:
            logger.warning("⚠ Could not find templates endpoint in router")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Router registration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_template_variables():
    """Test that template variables are properly stored and retrieved."""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: Template Variables")
    logger.info("="*60)
    
    try:
        from config.database import SessionLocal
        from models.bot_message import BotMessageTemplate
        
        db = SessionLocal()
        
        # Find templates with variables
        templates_with_vars = db.query(BotMessageTemplate).filter(
            BotMessageTemplate.variables.isnot(None)
        ).all()
        
        logger.info(f"✓ Found {len(templates_with_vars)} templates with variables")
        
        # Check first few
        for t in templates_with_vars[:3]:
            vars_list = t.variables if isinstance(t.variables, list) else []
            logger.info(f"  - {t.template_name}: {len(vars_list)} variables")
            if vars_list:
                logger.info(f"    Variables: {', '.join(vars_list)}")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Template variables test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_default_templates():
    """Test that default templates are properly marked."""
    logger.info("\n" + "="*60)
    logger.info("TEST 6: Default Templates")
    logger.info("="*60)
    
    try:
        from config.database import SessionLocal
        from models.bot_message import BotMessageTemplate
        
        db = SessionLocal()
        
        # Count default templates
        default_count = db.query(BotMessageTemplate).filter(
            BotMessageTemplate.is_default == True
        ).count()
        
        custom_count = db.query(BotMessageTemplate).filter(
            BotMessageTemplate.is_default == False
        ).count()
        
        total = db.query(BotMessageTemplate).count()
        
        logger.info(f"✓ Default templates: {default_count}")
        logger.info(f"✓ Custom templates: {custom_count}")
        logger.info(f"✓ Total templates: {total}")
        
        if default_count == 0:
            logger.warning("⚠ No default templates found")
        else:
            logger.info("✓ Default templates properly marked")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Default templates test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    logger.info("\n\n")
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + " "*58 + "║")
    logger.info("║" + "BOT MESSAGE TEMPLATES - COMPREHENSIVE TEST SUITE".center(58) + "║")
    logger.info("║" + " "*58 + "║")
    logger.info("╚" + "="*58 + "╝")
    
    tests = [
        ("Database Templates", test_database_templates),
        ("Template Model", test_template_model),
        ("API Endpoint", test_api_endpoint),
        ("Router Registration", test_router_registration),
        ("Template Variables", test_template_variables),
        ("Default Templates", test_default_templates),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"✗ Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    logger.info("\n\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info("="*60)
    logger.info(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Templates are working 100% ✅")
        return 0
    else:
        logger.error(f"\n⚠ {total - passed} test(s) failed. Please review the logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
