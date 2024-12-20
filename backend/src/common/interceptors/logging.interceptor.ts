import { 
  Injectable, 
  NestInterceptor, 
  ExecutionContext, 
  CallHandler, 
  Logger 
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger(LoggingInterceptor.name);

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const userEmail = request.user?.email || 'Unauthenticated';
    const method = request.method;
    const url = request.url;

    const now = Date.now();

    return next.handle().pipe(
      tap({
        next: (data) => {
          const responseTime = Date.now() - now;
          this.logger.log({
            message: 'Successful Request',
            method,
            url,
            userEmail,
            responseTime: `${responseTime}ms`,
            statusCode: context.switchToHttp().getResponse().statusCode
          });
        },
        error: (error) => {
          const responseTime = Date.now() - now;
          this.logger.error({
            message: 'Failed Request',
            method,
            url,
            userEmail,
            responseTime: `${responseTime}ms`,
            error: error.message,
            stack: error.stack
          });
        }
      })
    );
  }
}
