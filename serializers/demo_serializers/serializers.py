from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from api.v1.users.models import User
from api.v1.restaurants.models import Restaurant

from api.v1.menu.models import Item, Section


"""
A model serializer is just an abstraction
"""
class NonModelMinimalItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, max_length=200)
    user_id = serializers.IntegerField(required=True)
    section_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        item = Item.objects.create(**validated_data)
        return item

    def update(self, instance, validated_data):
        for key in validated_data:
            setattr(instance, key, validated_data.get('name'))
        instance.save()
        return instance


"""
Serializers can have very rich relationships that make the above possible 
"""
class MinimalItemSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all().values_list('id', flat=True))
    section_id = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all().values_list('id', flat=True))

    class Meta:
        model = Item
        fields = ('name', 'user_id', 'section_id')


"""
Read only fields can also be specified in model meta 
"""
class SectionSerializer(serializers.ModelSerializer):
    restaurant_id = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all().values_list('id', flat=True))
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all().values_list('id', flat=True))

    class Meta:
        model = Section
        fields = ('id', 'name', 'restaurant_id', 'user_id')
        read_only_fields = ('id',)


"""
You have to do more to handle nested serializers
"""
class MinimalItem2Serializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all().values_list('id', flat=True))
    section = SectionSerializer()

    def is_valid(self, raise_exception=False):
        user_id = self.initial_data.get("user_id")
        if user_id and 'section' in self.initial_data:
            self.initial_data['section']['user_id'] = user_id
        return super().is_valid(raise_exception)

    def create(self, validated_data):
        """
        Does not support writable nested fields by default.
        If we see this commonly: https://github.com/beda-software/drf-writable-nested
        Introduces a pk field that can be used
        """
        section_data = validated_data.pop('section')
        section_serializer = SectionSerializer(data=section_data)
        section_serializer.is_valid()
        section = section_serializer.save()
        validated_data["section_id"] = section.id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        section_data = validated_data.pop('section')

        if instance.section:
            section_serializer = SectionSerializer(instance.section,
                                                   section_data,
                                                   partial=True)
            section_serializer.is_valid()
            section = section_serializer.save()
        else:
            section_serializer = SectionSerializer(data=section_data)
            section_serializer.is_valid()
            section = section_serializer.save()

        updated_item = super().create(validated_data)
        updated_item.section = section
        updated_item.save()
        return updated_item

    class Meta:
        model = Item
        fields = ('name', 'user_id', 'section')


"""
However plugins are available to help you along the way 
"""
class MinimalItem3Serializer(WritableNestedModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all().values_list('id', flat=True))
    section = SectionSerializer()

    def is_valid(self, raise_exception=False):
        user_id = self.initial_data.get("user_id")
        if user_id and 'section' in self.initial_data:
            self.initial_data['section']['user_id'] = user_id
        return super().is_valid(raise_exception)

    class Meta:
        model = Item
        fields = ('name', 'user_id', 'section')


"""
Serializers are extensible 
"""
class ItemSerializer(MinimalItemSerializer):
    class Meta:
        model = Item
        fields = MinimalItemSerializer.Meta.fields
        fields += ('description', 'rating')


class ItemDisplaySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # should always be false?

    def get_user(self, _):
        return self.context.get('current_user')

    class Meta:
        model = Item
        exclude = ("choices",)


class ItemArchiveSerializer(serializers.Serializer):
    action = serializers.CharField()
    pass  # Model hierarchies could be associated here

    def validate_action(self, action):
        if not action:
            return action
        elif action == "delete":
            raise serializers.ValidationError("You Crazy")
        elif action == "unarchive":
            return action
        else:
            raise serializers.ValidationError("Unknown Action")

    class Meta:
        fields = ('action',)
