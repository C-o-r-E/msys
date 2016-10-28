from django.contrib import admin
from members.models import Member, MemberType, Membership, AccessBlock, AccessCard, TimeBlock, AccessGroup
from members.models import Promotion, Promo_item

admin.site.register( (Member,
                        MemberType,
                        Membership,
                        AccessBlock,
                        AccessCard,
                        TimeBlock,
                        AccessGroup,
                        Promotion,
                        Promo_item,
                        ) )

