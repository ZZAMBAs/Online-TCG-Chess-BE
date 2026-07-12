package org.zzambas.tcgonlinechessbe;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(
    properties =
        "spring.autoconfigure.exclude=org.springframework.boot.jdbc.autoconfigure.DataSourceAutoConfiguration")
class TcgOnlineChessBeApplicationTests {

  @Test
  void contextLoads() {}
}
