from django.contrib import admin
from members.models import Member, MemberType, Membership, AccessBlock, AccessCard, TimeBlock, AccessGroup, Promotion

admin.site.register( (Member,
                        MemberType,
                        Membership,
                        AccessBlock,
                        AccessCard,
                        TimeBlock,
                        AccessGroup,
                        Promotion,
                        ) )

