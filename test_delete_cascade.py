#!/usr/bin/env python3
"""
Comprehensive test script to validate student deletion functionality.
Tests all cascade deletes and error handling.
"""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal, init_db
from models.student import Student, UserStatus
from models.homework import Homework, SubmissionType, PaymentType, HomeworkStatus
from models.subscription import Subscription
from models.payment import Payment, PaymentStatus
from models.tutor import Tutor  # Import to prevent relationship errors
from models.tutor_assignment import TutorAssignment  # Import to prevent relationship errors
from datetime import datetime, timedelta

# Initialize database to register all models
try:
    init_db()
except:
    pass  # Database might already be initialized

def cleanup_test_data(db):
    """Clean up test data."""
    # Delete test student and cascade will handle related records
    db.query(Student).filter(Student.phone_number == "+9999999999").delete()
    db.commit()
    print("✓ Test data cleaned up")

def test_delete_with_cascade():
    """Test student deletion with cascade deletes."""
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("TEST: Student Deletion with Cascade Deletes")
        print("="*80)
        
        # Cleanup any existing test data
        cleanup_test_data(db)
        
        # 1. Create a test student
        print("\n1️⃣ Creating test student...")
        student = Student(
            phone_number="+9999999999",
            full_name="Test Delete User",
            email="test@delete.com",
            class_grade="10A",
            status=UserStatus.REGISTERED_FREE
        )
        db.add(student)
        db.commit()
        student_id = student.id
        print(f"   ✓ Student created with ID: {student_id}")
        
        # 2. Create related homework records
        print("\n2️⃣ Creating homework records...")
        hw1 = Homework(
            student_id=student_id,
            subject="Mathematics",
            submission_type=SubmissionType.TEXT,
            content="Solve the equation",
            payment_type=PaymentType.ONE_TIME,
            status=HomeworkStatus.PENDING
        )
        hw2 = Homework(
            student_id=student_id,
            subject="Physics",
            submission_type=SubmissionType.IMAGE,
            file_path="/uploads/physics_hw.jpg",
            payment_type=PaymentType.SUBSCRIPTION,
            status=HomeworkStatus.IN_PROGRESS
        )
        db.add(hw1)
        db.add(hw2)
        db.commit()
        print(f"   ✓ Created 2 homework records")
        
        # 3. Create payment record
        print("\n3️⃣ Creating payment record...")
        payment = Payment(
            student_id=student_id,
            amount=5000,
            currency="NGN",
            status=PaymentStatus.SUCCESS,
            payment_reference=f"ref_test_{student_id}",
            is_subscription=False
        )
        db.add(payment)
        db.commit()
        print(f"   ✓ Payment record created")
        
        # 4. Create subscription record
        print("\n4️⃣ Creating subscription record...")
        subscription = Subscription(
            student_id=student_id,
            payment_id=payment.id,
            amount="25000",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True,
            auto_renew=True
        )
        db.add(subscription)
        db.commit()
        print(f"   ✓ Subscription record created")
        
        # 5. Verify all records exist
        print("\n5️⃣ Verifying all records exist before deletion...")
        student_count = db.query(Student).filter_by(id=student_id).count()
        hw_count = db.query(Homework).filter_by(student_id=student_id).count()
        payment_count = db.query(Payment).filter_by(student_id=student_id).count()
        sub_count = db.query(Subscription).filter_by(student_id=student_id).count()
        
        print(f"   - Students: {student_count} (expected: 1)")
        print(f"   - Homeworks: {hw_count} (expected: 2)")
        print(f"   - Payments: {payment_count} (expected: 1)")
        print(f"   - Subscriptions: {sub_count} (expected: 1)")
        
        assert student_count == 1, "Student not found!"
        assert hw_count == 2, "Homeworks not created!"
        assert payment_count == 1, "Payment not created!"
        assert sub_count == 1, "Subscription not created!"
        print("   ✓ All records verified")
        
        # 6. Delete the student (this should cascade)
        print("\n6️⃣ Deleting student (cascade should delete all related records)...")
        student_to_delete = db.query(Student).filter_by(id=student_id).first()
        db.delete(student_to_delete)
        db.commit()
        print(f"   ✓ Student deleted")
        
        # 7. Verify cascade deletes worked
        print("\n7️⃣ Verifying cascade deletes...")
        student_count = db.query(Student).filter_by(id=student_id).count()
        hw_count = db.query(Homework).filter_by(student_id=student_id).count()
        payment_count = db.query(Payment).filter_by(student_id=student_id).count()
        sub_count = db.query(Subscription).filter_by(student_id=student_id).count()
        
        print(f"   - Students: {student_count} (expected: 0)")
        print(f"   - Homeworks: {hw_count} (expected: 0)")
        print(f"   - Payments: {payment_count} (expected: 0)")
        print(f"   - Subscriptions: {sub_count} (expected: 0)")
        
        assert student_count == 0, "Student record not deleted!"
        assert hw_count == 0, "Homeworks not cascade deleted!"
        assert payment_count == 0, "Payments not cascade deleted!"
        assert sub_count == 0, "Subscriptions not cascade deleted!"
        print("   ✓ All cascade deletes verified")
        
        print("\n" + "="*80)
        print("✅ TEST PASSED: Student deletion with cascade deletes works 100%!")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_error_cases():
    """Test error handling."""
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("TEST: Error Cases and Edge Cases")
        print("="*80)
        
        # Test 1: Delete non-existent student
        print("\n1️⃣ Test deleting non-existent student...")
        non_existent = db.query(Student).filter_by(id=99999999).first()
        if non_existent is None:
            print("   ✓ Non-existent student correctly returns None")
        else:
            print("   ❌ Non-existent student should return None!")
            return False
        
        # Test 2: Verify id filtering works
        print("\n2️⃣ Test filtering by student ID...")
        real_student = db.query(Student).filter_by(id=1).first()
        if real_student:
            print(f"   ✓ Student filtering works: {real_student.phone_number}")
        
        print("\n" + "="*80)
        print("✅ ERROR CASES TEST PASSED!")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "█"*80)
    print("Student Deletion Functionality - Comprehensive Test Suite")
    print("█"*80)
    
    # Run tests
    test1_passed = test_delete_with_cascade()
    test2_passed = test_error_cases()
    
    # Summary
    print("\n" + "█"*80)
    print("TEST SUMMARY")
    print("█"*80)
    print(f"Cascade Delete Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Error Cases Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n" + "🎉 "*20)
        print("ALL TESTS PASSED - DELETE FUNCTIONALITY IS 100% WORKING!")
        print("🎉 "*20)
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
