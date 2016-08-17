#include "event_logger.h"

#include <assert.h>
#include <time.h>
#include <stdio.h>

#if EVENT_LOG
static struct {
	FILE *logfile;
} event_logger_state;

#endif

void qcgc_event_logger_initialize(void) {
#if EVENT_LOG
	event_logger_state.logfile = fopen(LOGFILE, "w");
	qcgc_event_logger_log(EVENT_START_LOG, 0, NULL);

	if (event_logger_state.logfile == NULL)  {
		fprintf(stderr, "%s\n", "Failed to create logfile.");
	}
#endif
}

void qcgc_event_logger_destroy(void) {
#if EVENT_LOG
	qcgc_event_logger_log(EVENT_STOP_LOG, 0, NULL);

	if (event_logger_state.logfile != NULL) {
		fflush(event_logger_state.logfile);
		fclose(event_logger_state.logfile);
		event_logger_state.logfile = NULL;
	}
#endif
}

void qcgc_event_logger_log(enum event_e event, uint32_t additional_data_size,
		uint8_t *additional_data) {
#if EVENT_LOG
#if CHECKED
	assert((additional_data_size == 0) == (additional_data == NULL));
#endif // CHECKED
	struct {
		uint32_t sec;
		uint32_t nsec;
		uint8_t event_id;
		uint32_t additional_data_size;
	} __attribute__ ((packed)) log_entry;

	if (event_logger_state.logfile != NULL) {
		struct timespec t;
		clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t);

		log_entry.sec = (uint32_t) t.tv_sec;
		log_entry.nsec = (uint32_t) t.tv_nsec;
		log_entry.event_id = (uint8_t) event;
		log_entry.additional_data_size = additional_data_size;

		// The size and nmemb fields are flipped intentionally
		size_t result = 0;
		result = fwrite(&log_entry, sizeof(log_entry), 1,
				event_logger_state.logfile);
		if (result != 1) {
			fprintf(stderr, "%s\n", "Failed to write log entry.");
			qcgc_event_logger_destroy();
			return;
		}
		if (additional_data_size > 0) {
			result = fwrite(additional_data, additional_data_size, 1,
					event_logger_state.logfile);

			if (result != 1) {
				fprintf(stderr, "%s\n", "Failed to write additional data.");
				qcgc_event_logger_destroy();
				return;
			}
		}
	}

#endif // EVENT_LOG
}
