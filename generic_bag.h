#pragma once

#include <assert.h>
#include <stddef.h>
#include <stdlib.h>

#define DECLARE_BAG(name, type)												\
typedef struct name##_s {													\
	size_t size;															\
	size_t count;															\
	type items[];															\
} name##_t;																	\
																			\
name##_t *qcgc_##name##_create(size_t size);								\
name##_t *qcgc_##name##_add(name##_t *self, type item);						\
name##_t *qcgc_##name##_remove_index(name##_t *self, size_t index);

#define DEFINE_BAG(name, type)												\
static size_t name##_size(size_t size);										\
static name##_t *name##_grow(name##_t *self);								\
static name##_t *name##_shrink(name##_t *self);								\
																			\
name##_t *qcgc_##name##_create(size_t size) {								\
	name##_t *result = (name##_t *) malloc(name##_size(size));				\
	result->size = size;													\
	result->count = 0;														\
	return result;															\
}																			\
																			\
name##_t *qcgc_##name##_add(name##_t *self, type item) {					\
	if (self->count >= self->size) {										\
		self = name##_grow(self);											\
	}																		\
	self->items[self->count++] = item;										\
	return self;															\
}																			\
																			\
name##_t *qcgc_##name##_remove_index(name##_t *self, size_t index) {		\
	if (index + 1 < self->count) {											\
		self->items[index] = self->items[self->count - 1];					\
	}																		\
	self->count--;															\
																			\
	if (self->count < self->size / 4) {										\
		self = name##_shrink(self);											\
	}																		\
	return self;															\
}																			\
																			\
static name##_t *name##_grow(name##_t *self) {								\
	name##_t *new_self = (name##_t *) realloc(self,							\
			name##_size(self->size * 2));									\
	assert(new_self != NULL);												\
	self = new_self;														\
	self->size *= 2;														\
	return self;															\
}																			\
																			\
static name##_t *name##_shrink(name##_t *self) {							\
	name##_t *new_self = (name##_t *) realloc(self,							\
			name##_size(self->size / 2));									\
	assert(new_self != NULL);												\
	self = new_self;														\
	self->size /= 2;														\
	return self;															\
}																			\
																			\
static size_t name##_size(size_t size) {									\
	return sizeof(name##_t) + size * sizeof(type);							\
}
