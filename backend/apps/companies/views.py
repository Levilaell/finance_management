"""
Companies app views
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Company, CompanyUser, SubscriptionPlan
from .serializers import (
    CompanySerializer,
    CompanyUpdateSerializer,
    CompanyUserSerializer,
    InviteUserSerializer,
    SubscriptionPlanSerializer,
    UpgradeSubscriptionSerializer,
)

User = get_user_model()


class CompanyDetailView(generics.RetrieveAPIView):
    """Get company profile details"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CompanySerializer
    
    def get_object(self):
        return self.request.user.company


class CompanyUpdateView(generics.UpdateAPIView):
    """Update company profile"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CompanyUpdateSerializer
    
    def get_object(self):
        return self.request.user.company


class SubscriptionPlansView(generics.ListAPIView):
    """List available subscription plans"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')


class UpgradeSubscriptionView(APIView):
    """Upgrade company subscription"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = UpgradeSubscriptionSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        company = request.user.company
        new_plan = SubscriptionPlan.objects.get(
            id=serializer.validated_data['plan_id']
        )
        
        # Update subscription
        company.subscription_plan = new_plan
        company.subscription_status = 'active'
        company.save()
        
        # TODO: Integrate with payment provider
        
        return Response({
            'message': 'Subscription upgraded successfully',
            'new_plan': SubscriptionPlanSerializer(new_plan).data
        })


class CancelSubscriptionView(APIView):
    """Cancel company subscription"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        company = request.user.company
        
        if company.subscription_status != 'active':
            return Response({
                'error': 'No active subscription to cancel'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update subscription status
        company.subscription_status = 'cancelled'
        company.save()
        
        # TODO: Handle cancellation with payment provider
        
        return Response({
            'message': 'Subscription cancelled successfully'
        })


class CompanyUsersView(generics.ListAPIView):
    """List company users/team members"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CompanyUserSerializer
    
    def get_queryset(self):
        return CompanyUser.objects.filter(
            company=self.request.user.company
        ).select_related('user')


class InviteUserView(APIView):
    """Invite user to company"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        company = request.user.company
        
        # Check if company plan allows more users
        current_users = CompanyUser.objects.filter(
            company=company,
            is_active=True
        ).count() + 1  # +1 for owner
        
        if current_users >= company.subscription_plan.max_users:
            return Response({
                'error': 'User limit reached for current subscription plan'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = InviteUserSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        role = serializer.validated_data['role']
        permissions = serializer.validated_data.get('permissions', {})
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # TODO: Send invitation email to new user
            return Response({
                'message': 'Invitation sent to new user',
                'email': email
            })
        
        # Add existing user to company
        company_user = CompanyUser.objects.create(
            company=company,
            user=user,
            role=role,
            permissions=permissions,
            joined_at=timezone.now()
        )
        
        # TODO: Send notification to user
        
        return Response({
            'message': 'User added to company',
            'user': CompanyUserSerializer(company_user).data
        })


class RemoveUserView(APIView):
    """Remove user from company"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, user_id):
        company = request.user.company
        
        # Only owner can remove users
        if request.user != company.owner:
            return Response({
                'error': 'Only company owner can remove users'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            company_user = CompanyUser.objects.get(
                company=company,
                user_id=user_id
            )
        except CompanyUser.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Can't remove owner
        if company_user.user == company.owner:
            return Response({
                'error': 'Cannot remove company owner'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        company_user.delete()
        
        return Response({
            'message': 'User removed successfully'
        }, status=status.HTTP_204_NO_CONTENT)