#pragma once

#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "src/common/base/base.h"
#include "src/shared/metadata/k8s_objects.h"

namespace pl {
namespace md {

/**
 * CGroupMetadataReader is responsible for reading metsdata such as process info from
 * sys/fs and proc.
 *
 * TODO(zasgar/michelle): We need to reconcile this with the exising CGroupManager code as
 * we merge the metadata with the current cgroup code.
 */
class CGroupMetadataReader : public NotCopyable {
 public:
  CGroupMetadataReader() = delete;
  virtual ~CGroupMetadataReader() = default;

  // TODO(zasgar/michelle): Reconcile this constructor with the SysConfig changes when ready.
  CGroupMetadataReader(std::string_view sysfs_path, std::string_view proc_path,
                       int64_t ns_per_kernel_tick, int64_t clock_realtime_offset)
      : sysfs_path_(sysfs_path),
        proc_path_(proc_path),
        ns_per_kernel_tick_(ns_per_kernel_tick),
        clock_realtime_offset_(clock_realtime_offset) {}

  /**
   * ReadPIDList reads pids for a container running as part of a given pod.
   *
   * Note: that since this function contains inherent races with the system state and can return
   * errors when files fail to read because they have been deleted while the read was in progress.
   */
  virtual Status ReadPIDs(PodQOSClass qos_class, std::string_view pod_id,
                          std::string_view container_id,
                          absl::flat_hash_set<uint32_t>* pid_set) const;

  /**
   * @note With any of the PID functions there is an inherent race since the system is operating
   * independently of these functions. The Linux kernel is free to recycle PIDs so it's possible
   * (but unlikely) that multiple functions on the same PID will return inconsistent data.
   */

  /**
   * ReadPIDStartTime gets the start time for given PID.
   * @return the start time stamp in ns since unix epoch.
   * A time of zero means the read failed, or the process died.
   */
  virtual int64_t ReadPIDStartTime(uint32_t pid) const;

  /**
   * ReadPIDCmdline gets the command line for a given pid.
   * @return the cmdline with spaces. Empty string means the read failed or the process died.
   */
  virtual std::string ReadPIDCmdline(uint32_t pid) const;

 private:
  static std::string CGroupProcFilePath(std::string_view sysfs_prefix, PodQOSClass qos_class,
                                        std::string_view pod_id, std::string_view container_id);

  std::string sysfs_path_;
  std::string proc_path_;
  int64_t ns_per_kernel_tick_;
  int64_t clock_realtime_offset_;

  FRIEND_TEST(CGroupMetadataReaderTest, cgroup_proc_file_path);
};

}  // namespace md
}  // namespace pl
