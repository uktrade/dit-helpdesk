from ecs_logging import StdlibFormatter


class UserLogFormatter(StdlibFormatter):
    def format_to_ecs(self, record):
        result = super().format_to_ecs(record)

        if "user" in result:
            user = result.pop("user")
            result["user.id"] = user.username

        return result
