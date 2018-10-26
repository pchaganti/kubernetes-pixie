package common

import (
	"fmt"
	"time"

	"github.com/grpc-ecosystem/go-grpc-middleware"
	"github.com/grpc-ecosystem/go-grpc-middleware/auth"
	"github.com/grpc-ecosystem/go-grpc-middleware/logging/logrus"
	"github.com/grpc-ecosystem/go-grpc-middleware/tags"
	log "github.com/sirupsen/logrus"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func grpcInjectEnv(env BaseEnver) grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
		newCtx := context.WithValue(ctx, EnvKey, env)
		return handler(newCtx, req)
	}
}

func grpcAuthFunc(ctx context.Context) (context.Context, error) {
	token, err := grpc_auth.AuthFromMD(ctx, "bearer")
	if err != nil {
		return nil, err
	}
	env := ctx.Value(EnvKey).(BaseEnver)
	claims, err := env.GetBaseEnv().ParseJWTClaims(token)
	if err != nil {
		return nil, status.Errorf(codes.Unauthenticated, "invalid auth token: %v", err)
	}
	env.SetClaims(claims)
	return ctx, nil
}

// CreateGrpcServer creates a GRPC server with default middleware for our services.
func CreateGrpcServer(env BaseEnver) *grpc.Server {
	logrusEntry := log.NewEntry(log.StandardLogger())
	logrusOpts := []grpc_logrus.Option{
		grpc_logrus.WithDurationField(func(duration time.Duration) (key string, value interface{}) {
			return "time", fmt.Sprintf("%.2fms", float64(duration.Nanoseconds())/1.0E6)
		}),
	}
	grpc_logrus.ReplaceGrpcLogger(logrusEntry)
	grpcServer := grpc.NewServer(
		grpc_middleware.WithUnaryServerChain(
			grpc_ctxtags.UnaryServerInterceptor(),
			grpcInjectEnv(env),
			grpc_logrus.UnaryServerInterceptor(logrusEntry, logrusOpts...),
			grpc_auth.UnaryServerInterceptor(grpcAuthFunc),
		),
	)

	return grpcServer
}
