#pragma once

#include "config.h"

#include <stddef.h>
#include <stdint.h>

/**
 * All events
 */
enum event_e {
	EVENT_START_LOG,
	EVENT_STOP_LOG,
};

/**
 * Initialize logger
 */
void qcgc_event_logger_initialize(void);

/**
 * Destroy logger
 */
void qcgc_event_logger_destroy(void);

/**
 * Log event
 */
void qcgc_event_logger_log(enum event_e event, uint32_t additional_data_size,
		uint8_t *additional_data);
