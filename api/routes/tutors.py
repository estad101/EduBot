"""
Tutor routes - endpoints for tutors to manage assignments and submit solutions.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from schemas.response import StandardResponse
from services.tutor_service import TutorService
from models.tutor_assignment import AssignmentStatus
from config.database import get_db
from utils.logger import get_logger
import json

router = APIRouter(prefix="/api/tutors", tags=["tutors"])
logger = get_logger("tutors_route")


@router.get("/{tutor_id}/assignments")
async def get_tutor_assignments(
    tutor_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get assignments for a tutor.
    
    Query params:
    - status: Filter by status (PENDING, ASSIGNED, IN_PROGRESS, COMPLETED)
    """
    try:
        # Verify tutor exists
        tutor = TutorService.get_tutor_by_id(db, tutor_id)
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor not found")

        # Get assignments
        status_enum = None
        if status:
            try:
                status_enum = AssignmentStatus(status.upper())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}"
                )

        assignments = TutorService.get_assignments_by_tutor(
            db, tutor_id, status=status_enum
        )

        # Format response
        assignments_data = []
        for assignment in assignments:
            homework = assignment.homework
            assignments_data.append({
                "assignment_id": assignment.id,
                "homework_id": homework.id,
                "subject": homework.subject,
                "submission_type": homework.submission_type.value,
                "content": homework.content,
                "file_path": homework.file_path,
                "student_name": homework.student.full_name,
                "student_email": homework.student.email,
                "status": assignment.status.value,
                "assigned_at": assignment.assigned_at.isoformat(),
                "solution": {
                    "id": assignment.solution.id,
                    "text": assignment.solution.solution_text,
                    "file_path": assignment.solution.solution_file_path,
                    "video_url": assignment.solution.video_url,
                    "submitted_at": assignment.solution.submitted_at.isoformat(),
                } if assignment.solution else None,
            })

        return StandardResponse(
            status="success",
            message=f"Found {len(assignments)} assignments",
            data=assignments_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tutor assignments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{tutor_id}/assignments/{assignment_id}/submit-solution")
async def submit_solution(
    tutor_id: int,
    assignment_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Submit a solution for assigned homework.
    
    Request body:
    {
        "solution_text": "Step-by-step explanation...",
        "solution_file_path": "/path/to/solution.jpg",
        "video_url": "https://youtube.com/..."  // optional
    }
    """
    try:
        # Verify tutor exists
        tutor = TutorService.get_tutor_by_id(db, tutor_id)
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor not found")

        # Verify assignment exists and belongs to tutor
        assignment = TutorService.get_assignment_by_id(db, assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")

        if assignment.tutor_id != tutor_id:
            raise HTTPException(
                status_code=403,
                detail="Assignment does not belong to this tutor"
            )

        # Parse request
        body = await request.json()
        solution_text = body.get("solution_text")
        solution_file_path = body.get("solution_file_path")
        video_url = body.get("video_url")

        # Validate at least one solution method
        if not solution_text and not solution_file_path and not video_url:
            raise HTTPException(
                status_code=400,
                detail="At least one of solution_text, solution_file_path, or video_url is required"
            )

        # Submit solution
        solution = TutorService.submit_solution(
            db,
            assignment_id=assignment_id,
            solution_text=solution_text,
            solution_file_path=solution_file_path,
            video_url=video_url,
        )

        # Send WhatsApp notification to student
        try:
            from services.whatsapp_service import WhatsAppService
            student = assignment.homework.student
            
            notification_text = (
                f"📚 Solution received from your tutor for {assignment.homework.subject}!\n\n"
            )
            
            if solution_text:
                notification_text += f"📖 Explanation:\n{solution_text}\n\n"
            
            if solution_file_path:
                notification_text += f"📎 Solution document attached\n\n"
            
            if video_url:
                notification_text += f"🎥 Video walkthrough: {video_url}\n\n"
            
            notification_text += "Thank you for using our service!"
            
            await WhatsAppService.send_message(
                phone_number=student.phone_number,
                message_type="text",
                text=notification_text,
            )
            
            logger.info(f"Sent solution notification to student {student.id}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp notification: {str(e)}")
            # Don't fail the request if notification fails

        return StandardResponse(
            status="success",
            message="Solution submitted successfully",
            data={
                "solution_id": solution.id,
                "assignment_id": assignment_id,
                "submitted_at": solution.submitted_at.isoformat(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting solution: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{tutor_id}")
async def get_tutor_profile(
    tutor_id: int,
    db: Session = Depends(get_db),
):
    """Get tutor profile."""
    try:
        tutor = TutorService.get_tutor_by_id(db, tutor_id)
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor not found")

        return StandardResponse(
            status="success",
            message="Tutor profile retrieved",
            data={
                "id": tutor.id,
                "full_name": tutor.full_name,
                "email": tutor.email,
                "phone_number": tutor.phone_number,
                "subjects": tutor.subjects,
                "bio": tutor.bio,
                "is_active": tutor.is_active,
                "created_at": tutor.created_at.isoformat(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tutor profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
