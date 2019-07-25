from internal.service.logger.service import Logger


class LoggerFactory:
    def get_logger_service(self):
        return Logger()